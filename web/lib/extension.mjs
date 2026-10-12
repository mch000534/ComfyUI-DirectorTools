import { syncedSize } from './geometry.mjs?v=0.8.3';
import { createViewport } from './viewport.mjs?v=0.8.3';

const cameras = new WeakMap();
const installed = Symbol('DirectorToolsPanoramaViewer.extension');

export function installCamera(nodeType, api, isConfiguring = () => false) {
    const prototype = nodeType.prototype;
    if (prototype[installed]) return;
    prototype[installed] = true;
    const previousCreated = prototype.onNodeCreated;
    prototype.onNodeCreated = function (...args) {
        const result = previousCreated?.apply(this, args);
        const camera = createViewport(this, api);
        cameras.set(this, camera);
        for (const name of ['aspect_ratio','width','height','center_x','center_y','zoom','projection','camera_height']) {
            const widget = this.widgets.find(w => w.name === name);
            const previousCallback = widget.callback;
            const node = this;
            widget.callback = function (...callbackArgs) {
                const callbackResult = previousCallback?.apply(this, callbackArgs);
                if (['aspect_ratio','width','height'].includes(name)) {
                    const get = key => node.widgets.find(w => w.name === key);
                    const [width, height] = syncedSize(get('aspect_ratio').value, Number(get('width').value), Number(get('height').value), name);
                    get('width').value = width; get('height').value = height;
                }
                camera.sync(); node.setDirtyCanvas?.(true, true);
                return callbackResult;
            };
        }
        const dom = this.addDOMWidget('director_tools_panorama_viewport', 'director_tools_panorama', camera.element, {
            serialize: false, hideOnZoom: false,
            getMinHeight: () => 604, getMaxHeight: () => 604,
        });
        dom.computeSize = width => [width, 604];
        dom.onRemove = () => camera.destroy();
        this.setSize([Math.max(this.size[0], 500), Math.max(this.size[1], 888)]);
        return result;
    };
    const previousExecuted = prototype.onExecuted;
    prototype.onExecuted = function (message, ...args) {
        const result = previousExecuted?.call(this, message, ...args);
        const preview = message?.director_tools_panorama?.[0];
        if (preview) {
            this.properties.director_tools_panorama_preview = preview;
            cameras.get(this)?.loadPreview(preview);
        }
        return result;
    };
    const previousConfigure = prototype.onConfigure;
    prototype.onConfigure = function (...args) {
        const result = previousConfigure?.apply(this, args);
        // V0.1 workflows have six numeric/combo widget values and no projection.
        if (Array.isArray(args[0]?.widgets_values) && args[0].widgets_values.length === 6) {
            this.widgets.find(w=>w.name==='projection').value = 'Flat';
        }
        if (Array.isArray(args[0]?.widgets_values) && args[0].widgets_values.length < 8) {
            this.widgets.find(w=>w.name==='camera_height').value = 0;
        }
        cameras.get(this)?.loadPreview(this.properties.director_tools_panorama_preview);
        cameras.get(this)?.restore();
        this.setSize([Math.max(this.size[0],500),Math.max(this.size[1],888)]);
        return result;
    };
    const previousConnection = prototype.onConnectionsChange;
    prototype.onConnectionsChange = function (type, slot, ...args) {
        const result = previousConnection?.call(this, type, slot, ...args);
        if (type === 1 && slot === 0 && !isConfiguring()) {
            delete this.properties.director_tools_panorama_preview;
            cameras.get(this)?.clear();
        }
        return result;
    };
    const previousRemoved = prototype.onRemoved;
    prototype.onRemoved = function (...args) {
        cameras.get(this)?.destroy(); cameras.delete(this);
        return previousRemoved?.apply(this, args);
    };
}
