// Own headless browser and isolated ComfyUI test instance; never queues work.
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const {chromium} = createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE || 'playwright');
const browser = await chromium.launch({headless: true, channel: process.env.BROWSER_CHANNEL || 'chrome'});
try {
    const page = await browser.newPage({viewport: {width: 1200, height: 900}});
    await page.goto(process.env.COMFY_TEST_URL || 'http://127.0.0.1:8199');
    await page.waitForFunction(() => window.app && window.LiteGraph?.registered_node_types?.DirectorToolsAssetPrompt);
    await page.waitForLoadState('networkidle');
    const result = await page.evaluate(async () => {
        const app = window.app;
        const node = window.LiteGraph.createNode('DirectorToolsAssetPrompt');
        app.graph.clear(); app.graph.add(node);
        node.pos = [100, 100];
        const get = key => node.widgets.find(w => w.name === key);
        const visible = n => n.widgets.filter(w => !w.hidden && !w.options?.hidden).map(w => w.name);
        const character = visible(node);
        get('custom_prompt').value = '角色 description';
        get('character_layout').value = 'Three views + face close-up';
        get('background').value = 'White';
        get('environment').value = 'Outdoor';
        get('lighting').value = 'Natural light';
        get('aspect_ratio').value = '16:9';
        get('asset_type').value = 'Panorama';
        get('asset_type').callback('Panorama');
        const panorama = visible(node);
        const values = Object.fromEntries(node.widgets.map(w => [w.name, w.value]));
        const graph = app.graph.serialize();
        await app.loadGraphData(graph);
        const restored = app.graph.nodes.find(n => n.type === 'DirectorToolsAssetPrompt');
        const loadedPanorama = visible(restored);
        const loadedValues = Object.fromEntries(restored.widgets.map(w => [w.name, w.value]));
        const api = await app.graphToPrompt();
        const mode = restored.widgets.find(w => w.name === 'asset_type');
        mode.value = 'Character'; mode.callback('Character');
        const switchedBack = visible(restored);
        const backValues = Object.fromEntries(restored.widgets.map(w => [w.name, w.value]));
        mode.value = 'Panorama'; mode.callback('Panorama');
        app.canvas.ds.scale = 1;
        app.canvas.ds.offset = [100, 100];
        app.canvas.setDirty(true, true);
        return {character, panorama, loadedPanorama, values, loadedValues, switchedBack, backValues, inputs: api.output[String(restored.id)]?.inputs};
    });
    const common = ['custom_prompt', 'asset_type', 'language', 'style'];
    const character = [...common, 'character_layout', 'background', 'expression', 'aspect_ratio'].sort();
    const panorama = [...common, 'environment', 'time_of_day', 'lighting'].sort();
    assert.deepEqual(result.character.sort(), character);
    assert.deepEqual(result.panorama.sort(), panorama);
    assert.deepEqual(result.loadedPanorama.sort(), panorama);
    assert.deepEqual(result.switchedBack.sort(), character);
    assert.deepEqual(result.loadedValues, result.values);
    assert.deepEqual(result.backValues, {...result.values, asset_type: 'Character'});
    assert.deepEqual(result.inputs, result.values);
    await page.screenshot({path: new URL('../docs/asset-prompt-panorama.png', import.meta.url).pathname});
    const grid = await page.evaluate(async () => {
        const app = window.app;
        let node = app.graph.nodes.find(n => n.type === 'DirectorToolsAssetPrompt');
        const visible = () => node.widgets.filter(w => !w.hidden && !w.options?.hidden).map(w => w.name);
        const set = (name, value) => { const w = node.widgets.find(w => w.name === name); w.value = value; w.callback?.(value); };
        set('asset_type', 'Nine-grid asset · 九宮格資產');
        const views = {};
        for (const type of ['Character', 'Scene', 'Prop']) {
            set('grid_asset_type', type); views[type] = visible();
        }
        const values = Object.fromEntries(node.widgets.map(w => [w.name, w.value]));
        await app.loadGraphData(app.graph.serialize());
        node = app.graph.nodes.find(n => n.type === 'DirectorToolsAssetPrompt');
        const loaded = visible();
        const loadedValues = Object.fromEntries(node.widgets.map(w => [w.name, w.value]));
        const api = await app.graphToPrompt();
        // A v0.9 workflow has only the original ten widget values.
        const oldGraph = app.graph.serialize();
        oldGraph.nodes[0].widgets_values.splice(10);
        oldGraph.nodes[0].widgets_values[1] = 'Panorama';
        await app.loadGraphData(oldGraph);
        node = app.graph.nodes.find(n => n.type === 'DirectorToolsAssetPrompt');
        const oldValues = Object.fromEntries(node.widgets.map(w => [w.name, w.value]));
        set('asset_type', 'Nine-grid asset · 九宮格資產'); set('grid_asset_type', 'Prop');
        return {views, values, loaded, loadedValues, inputs: api.output[String(node.id)]?.inputs, oldValues};
    });
    const expectedGrid = {
        Character: [...common, 'grid_asset_type', 'background', 'expression', 'aspect_ratio'],
        Scene: [...common, 'grid_asset_type', 'environment', 'time_of_day', 'lighting', 'aspect_ratio'],
        Prop: [...common, 'grid_asset_type', 'background', 'lighting', 'aspect_ratio'],
    };
    for (const type of Object.keys(expectedGrid)) assert.deepEqual(grid.views[type].sort(), expectedGrid[type].sort());
    assert.deepEqual(grid.loaded.sort(), expectedGrid.Prop.sort());
    assert.deepEqual(grid.loadedValues, grid.values);
    assert.deepEqual(grid.inputs, grid.values);
    assert.deepEqual(grid.oldValues, {...grid.values, asset_type: 'Panorama', grid_asset_type: 'Character', aspect_ratio: 'Auto'});
    await page.screenshot({path: new URL('../docs/asset-prompt-nine-grid.png', import.meta.url).pathname});
    console.log('Actual ComfyUI: all grid asset types, immediate visibility, workflow reload, old workflow compatibility and API serialization pass; no queued work.');
} finally {
    await browser.close();
}
