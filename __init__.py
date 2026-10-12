from .nodes import DirectorToolsPanoramaViewer
from .director_tools import DirectorToolsGridSplit
from .shot_nodes import DirectorToolsBatchPanorama, DirectorToolsContactSheet
from .panorama_shift import DirectorToolsPanoramaShift
from .asset_prompt import DirectorToolsAssetPrompt

NODE_CLASS_MAPPINGS = {'DirectorToolsPanoramaViewer': DirectorToolsPanoramaViewer, 'DirectorToolsGridSplit': DirectorToolsGridSplit,
                       'DirectorToolsBatchPanorama': DirectorToolsBatchPanorama, 'DirectorToolsContactSheet': DirectorToolsContactSheet,
                       'DirectorToolsPanoramaShift': DirectorToolsPanoramaShift,
                       'DirectorToolsAssetPrompt': DirectorToolsAssetPrompt}
NODE_DISPLAY_NAME_MAPPINGS = {'DirectorToolsPanoramaViewer': 'Director Tools · Panorama viewer', 'DirectorToolsGridSplit': 'Director Tools · Grid Split',
                              'DirectorToolsBatchPanorama': 'Director Tools · Batch Panorama', 'DirectorToolsContactSheet': 'Director Tools · Contact Sheet',
                              'DirectorToolsPanoramaShift': 'Director Tools · Panorama Shift',
                              'DirectorToolsAssetPrompt': 'Director Tools · Asset Prompt'}
WEB_DIRECTORY = './web'

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
