import { app } from '../../scripts/app.js';
import { installAssetPromptControls } from './lib/asset_prompt_controls.mjs?v=0.10.1';

app.registerExtension({
    name: 'DirectorToolsAssetPrompt.ModeFields',
    beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name === 'DirectorToolsAssetPrompt') {
            installAssetPromptControls(nodeType);
        }
    },
});
