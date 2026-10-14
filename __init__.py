from .nodes import DirectorToolsPanoramaViewer
from .director_tools import DirectorToolsGridSplit
from .shot_nodes import DirectorToolsBatchPanorama, DirectorToolsContactSheet
from .panorama_shift import DirectorToolsPanoramaShift
from .asset_prompt import DirectorToolsAssetPrompt

NODE_CLASS_MAPPINGS = {'DirectorToolsPanoramaViewer': DirectorToolsPanoramaViewer, 'DirectorToolsGridSplit': DirectorToolsGridSplit,
                       'DirectorToolsBatchPanorama': DirectorToolsBatchPanorama, 'DirectorToolsContactSheet': DirectorToolsContactSheet,
                       'DirectorToolsPanoramaShift': DirectorToolsPanoramaShift,
                       'DirectorToolsAssetPrompt': DirectorToolsAssetPrompt}
NODE_DISPLAY_NAME_MAPPINGS = {'DirectorToolsPanoramaViewer': 'Super Director Tools · Panorama viewer', 'DirectorToolsGridSplit': 'Super Director Tools · Grid Split',
                              'DirectorToolsBatchPanorama': 'Super Director Tools · Batch Panorama', 'DirectorToolsContactSheet': 'Super Director Tools · Contact Sheet',
                              'DirectorToolsPanoramaShift': 'Super Director Tools · Panorama Shift',
                              'DirectorToolsAssetPrompt': 'Super Director Tools · Asset Prompt'}
WEB_DIRECTORY = './web'

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
