import { app } from '../../scripts/app.js';
import { api } from '../../scripts/api.js';
import { installCamera } from './lib/extension.mjs?v=0.8.3';

app.registerExtension({
    name: 'DirectorToolsPanoramaViewer.FixedViewport',
    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === 'DirectorToolsPanoramaViewer') {
            installCamera(nodeType, api, () => Boolean(app.configuringGraph));
        }
    },
});
