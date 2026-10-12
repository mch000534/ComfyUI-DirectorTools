import test from 'node:test';
import assert from 'node:assert/strict';
import * as controls from '../web/lib/asset_prompt_controls.mjs';

const names = ['custom_prompt', 'asset_type', 'language', 'character_layout', 'style', 'background', 'expression', 'environment', 'time_of_day', 'lighting', 'grid_asset_type', 'aspect_ratio'];
function fixture() {
    class Node {
        constructor() {
            this.size = [400, 600];
            this.widgets = names.map(name => ({name, value: name === 'asset_type' ? 'Character' : `${name} value`, type: 'combo', options: {values: ['a', 'b']}, computeSize: () => [200, 20]}));
            this.onNodeCreated();
        }
        computeSize() { return [400, 60 + this.widgets.reduce((sum, w) => sum + w.computeSize()[1] + 4, 0)]; }
        setSize(size) { this.size = size; }
        setDirtyCanvas() { this.dirty = true; }
        onNodeCreated() { this.created = true; }
        onConfigure() { this.configured = true; }
    }
    controls.installAssetPromptControls(Node);
    return new Node();
}
const visible = node => node.widgets.filter(w => !w.hidden && !w.options.hidden).map(w => w.name);

test('creation shows shared and character fields, collapsing panorama rows', () => {
    const node = fixture();
    assert.ok(node.created);
    assert.deepEqual(visible(node), ['custom_prompt', 'asset_type', 'language', 'character_layout', 'style', 'background', 'expression', 'aspect_ratio']);
    assert.equal(node.size[1], 252);
});

test('mode callback immediately switches rows without changing values or serialization', () => {
    const node = fixture();
    const widgets = [...node.widgets];
    const originals = widgets.map(w => ({value: w.value, type: w.type, options: {...w.options}, computeSize: w.computeSize}));
    const mode = widgets.find(w => w.name === 'asset_type');
    for (let i = 0; i < 3; i++) {
        mode.value = 'Panorama'; mode.callback('Panorama');
        assert.deepEqual(visible(node), ['custom_prompt', 'asset_type', 'language', 'style', 'environment', 'time_of_day', 'lighting']);
        mode.value = 'Character'; mode.callback('Character');
    }
    assert.deepEqual(node.widgets, widgets);
    widgets.forEach((w, i) => {
        assert.equal(w.value, originals[i].value);
        assert.equal(w.type, originals[i].type);
        if (['character_layout', 'background', 'expression'].includes(w.name)) {
            assert.deepEqual(w.options, originals[i].options);
            assert.equal(w.computeSize, originals[i].computeSize);
            assert.equal(Object.hasOwn(w, 'hidden'), false);
        }
    });
});

test('workflow configure restores visibility for saved mode and keeps existing hooks', () => {
    const node = fixture();
    node.widgets.find(w => w.name === 'asset_type').value = 'Panorama';
    node.onConfigure({});
    assert.ok(node.configured);
    assert.equal(visible(node).includes('character_layout'), false);
    assert.equal(visible(node).includes('lighting'), true);
    assert.ok(node.dirty);
});

test('installation is idempotent and mode callback preserves existing callback', () => {
    let calls = 0;
    class Node {
        onNodeCreated() { this.widgets = [{name: 'asset_type', value: 'Character', callback() { calls++; return 42; }}]; }
    }
    controls.installAssetPromptControls(Node);
    const created = Node.prototype.onNodeCreated;
    controls.installAssetPromptControls(Node);
    assert.equal(Node.prototype.onNodeCreated, created);
    const node = new Node(); node.onNodeCreated();
    assert.equal(node.widgets[0].callback('Character'), 42);
    assert.equal(calls, 1);
});

test('nine-grid type switches show only shared and asset-specific fields', () => {
    const node = fixture();
    const get = name => node.widgets.find(w => w.name === name);
    get('asset_type').value = 'Nine-grid asset · 九宮格資產';
    const expected = {
        Character: ['custom_prompt', 'asset_type', 'language', 'style', 'background', 'expression', 'grid_asset_type', 'aspect_ratio'],
        Scene: ['custom_prompt', 'asset_type', 'language', 'style', 'environment', 'time_of_day', 'lighting', 'grid_asset_type', 'aspect_ratio'],
        Prop: ['custom_prompt', 'asset_type', 'language', 'style', 'background', 'lighting', 'grid_asset_type', 'aspect_ratio'],
    };
    for (const type of ['Character', 'Scene', 'Prop']) {
        get('grid_asset_type').value = type;
        get('asset_type').callback(get('asset_type').value);
        get('grid_asset_type').callback(type);
        assert.deepEqual(visible(node), expected[type]);
    }
    get('asset_type').value = 'Panorama'; get('asset_type').callback('Panorama');
    assert.equal(get('grid_asset_type').hidden, true);
    assert.equal(get('grid_asset_type').value, 'Prop');
    assert.equal(get('aspect_ratio').hidden, true);
    const previous = get('aspect_ratio').value;
    get('asset_type').value = 'Character'; get('asset_type').callback('Character');
    assert.equal(get('aspect_ratio').hidden, undefined);
    assert.equal(get('aspect_ratio').value, previous);
});
