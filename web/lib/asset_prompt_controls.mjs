const installed = Symbol('DirectorToolsAssetPrompt.ModeFields');
const hiddenState = new WeakMap();
const characterFields = ['character_layout', 'background', 'expression'];
const panoramaFields = ['environment', 'time_of_day', 'lighting'];
const gridMode = 'Nine-grid asset · 九宮格資產';
const hiddenSize = () => [0, -4];

function snapshot(object, key) {
    return Object.getOwnPropertyDescriptor(object, key);
}

function restore(object, key, descriptor) {
    if (descriptor) Object.defineProperty(object, key, descriptor);
    else delete object[key];
}

function setHidden(widget, hidden) {
    if (hidden) {
        if (hiddenState.has(widget)) return;
        const state = {
            hidden: snapshot(widget, 'hidden'),
            computeSize: snapshot(widget, 'computeSize'),
            options: snapshot(widget, 'options'),
            optionsObject: widget.options ?? {},
            optionsHidden: widget.options ? snapshot(widget.options, 'hidden') : undefined,
        };
        hiddenState.set(widget, state);
        widget.options = state.optionsObject;
        widget.hidden = true;
        widget.options.hidden = true;
        widget.computeSize = hiddenSize;
    } else {
        const state = hiddenState.get(widget);
        if (!state) return;
        restore(widget, 'hidden', state.hidden);
        // A converted input may replace computeSize while the field is hidden.
        if (widget.computeSize === hiddenSize) restore(widget, 'computeSize', state.computeSize);
        restore(state.optionsObject, 'hidden', state.optionsHidden);
        if (widget.options === state.optionsObject) restore(widget, 'options', state.options);
        hiddenState.delete(widget);
    }
}

export function syncAssetPromptFields(node) {
    const mode = node.widgets?.find(w => w.name === 'asset_type')?.value;
    if (!['Character', 'Panorama', gridMode].includes(mode)) return;
    let visibleFields = mode === 'Character' ? characterFields : panoramaFields;
    if (mode === gridMode) {
        const asset = node.widgets.find(w => w.name === 'grid_asset_type')?.value ?? 'Character';
        visibleFields = asset === 'Scene' ? panoramaFields :
            asset === 'Prop' ? ['background', 'lighting'] : ['background', 'expression'];
    }
    for (const widget of node.widgets) {
        if ([...characterFields, ...panoramaFields].includes(widget.name)) {
            setHidden(widget, !visibleFields.includes(widget.name));
        }
        if (widget.name === 'grid_asset_type') setHidden(widget, mode !== gridMode);
        if (widget.name === 'aspect_ratio') setHidden(widget, mode === 'Panorama');
    }
    // Nodes 2.0 snapshots widgets for Vue rendering. Invalidate without replacing
    // widget objects, order, values, types or serialization functions.
    node.widgets = [...node.widgets];
    if (node.computeSize && node.setSize) {
        const size = node.computeSize();
        node.setSize([Math.max(node.size?.[0] ?? size[0], size[0]), size[1]]);
    }
    node.setDirtyCanvas?.(true, true);
}

export function installAssetPromptControls(nodeType) {
    const prototype = nodeType.prototype;
    if (prototype[installed]) return;
    prototype[installed] = true;
    const created = prototype.onNodeCreated;
    prototype.onNodeCreated = function (...args) {
        const result = created?.apply(this, args);
        for (const name of ['asset_type', 'grid_asset_type']) {
            const mode = this.widgets?.find(w => w.name === name);
            if (!mode) continue;
            const callback = mode.callback;
            const node = this;
            mode.callback = function (...values) {
                const result = callback?.apply(this, values);
                syncAssetPromptFields(node);
                return result;
            };
        }
        syncAssetPromptFields(this);
        return result;
    };
    const configured = prototype.onConfigure;
    prototype.onConfigure = function (...args) {
        const result = configured?.apply(this, args);
        syncAssetPromptFields(this);
        return result;
    };
}
