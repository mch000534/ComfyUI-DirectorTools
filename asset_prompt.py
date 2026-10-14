"""Local bilingual prompt assembly for characters, panoramas and asset grids."""
from .grid_asset_prompt import GRID_MODE, GRID_ASSET_TYPES, grid_asset_prompt

# Values are stable workflow/API identifiers; tuples contain English and Chinese text.
OPTIONS = {
    'style': {
        'None': ('', ''),
        'Photorealistic': ('Photorealistic rendering with natural, detailed materials.', '寫實風格，材質自然且細節清晰。'),
        'Cinematic': ('Cinematic visual style with coherent color grading.', '電影感視覺風格，色調一致。'),
        'Anime': ('Anime illustration style with clean linework.', '動漫插畫風格，線條清晰。'),
        '3D stylized': ('Stylized 3D rendering.', '風格化 3D 渲染。'),
        'Concept art': ('Detailed concept art.', '細緻的概念設計美術。'),
    },
    'background': {
        'None': ('', ''),
        'White': ('Use a plain white background.', '使用純白色背景。'),
        'Gray': ('Use a plain gray background.', '使用純灰色背景。'),
        'Simple studio': ('Use a simple uncluttered studio background.', '使用簡潔、無雜物的攝影棚背景。'),
    },
    'expression': {
        'None': ('', ''),
        'Neutral': ('Use a neutral expression.', '使用中性表情。'),
        'Happy': ('Use a happy expression.', '使用開心表情。'),
        'Serious': ('Use a serious expression.', '使用嚴肅表情。'),
    },
    'environment': {
        'None': ('', ''),
        'Indoor': ('Create an indoor environment.', '建立室內環境。'),
        'Outdoor': ('Create an outdoor environment.', '建立室外環境。'),
    },
    'time_of_day': {
        'None': ('', ''),
        'Dawn': ('Set the scene at dawn.', '場景時間為黎明。'),
        'Day': ('Set the scene during daytime.', '場景時間為白天。'),
        'Sunset': ('Set the scene at sunset.', '場景時間為日落。'),
        'Night': ('Set the scene at night.', '場景時間為夜晚。'),
    },
    'lighting': {
        'None': ('', ''),
        'Natural light': ('Use natural light with consistent direction and exposure.', '使用自然光，光源方向與曝光一致。'),
        'Soft light': ('Use soft light with gentle shadows.', '使用柔和光線與柔和陰影。'),
        'Dramatic light': ('Use dramatic light with coherent highlights and shadows.', '使用戲劇化光線，明暗與陰影合理一致。'),
    },
}

LAYOUTS = ['Three views', 'Three views + face close-up', 'Single full body']
ASPECT_RATIOS = ['Auto', '1:1', '16:9', '9:16', '4:3', '3:4', '3:2', '2:3', '2:1', '21:9']
LAYOUT_PROMPTS = {
    'Three views': (
        'Create one character reference sheet with three full-body views arranged left to right: front, side and back. '
        'Depict the same character at the same scale in a consistent neutral standing pose in all views. '
        'Keep each view separate, aligned and fully visible from head to feet, with space between views.',
        '製作一張角色設定圖，從左至右排列正面、側面、背面三個全身視圖。'
        '所有視圖呈現同一角色、相同比例及一致的自然站姿，各視圖分開對齊，完整顯示頭部至腳部，保留適當間距。',
    ),
    'Single full body': (
        'Create one full-body character image, showing one character completely from head to feet, with clear readable details.',
        '製作一張單人全身角色圖，完整顯示頭部至腳部，角色細節清晰可辨。',
    ),
}

CHARACTER_CONSISTENCY = (
    'Preserve the described identity, facial features, hairstyle, body proportions, costume, colors and accessories consistently. '
    'Keep anatomy coherent and details sharp. Do not introduce unrelated characters, text, labels, logos or watermarks.',
    '維持描述中的角色身份、五官、髮型、身體比例、服裝、顏色及配件一致。人體結構合理，細節清晰。'
    '不要加入無關角色、文字、標籤、標誌或浮水印。',
)
PANORAMA_PROMPT = (
    'Create one complete 360-degree horizontal by 180-degree vertical equirectangular panorama with a 2:1 aspect ratio. '
    'The outer left and right edges must connect seamlessly as a continuous horizontal wraparound: '
    'match structures, object contours, textures, colors, exposure and lighting across the join. '
    'Maintain spatially coherent scene geometry, a consistent horizon and lighting direction throughout the full environment. '
    'Use correct equirectangular projection, including its expected stretching near the poles; '
    'do not substitute a perspective view, fisheye view, cropped wide image or little-planet projection. '
    'Keep detail clear without stitching artifacts, duplicate objects or abrupt seam transitions. '
    'Output a single panorama without panels, borders, text, logos or watermarks.',
    '製作一張完整的 360° 水平 × 180° 垂直等距柱狀投影全景圖，寬高比為 2:1。'
    '左右外側邊緣必須首尾無縫相連，形成連續的水平環繞空間；接合處的結構、物件輪廓、紋理、顏色、曝光及光線必須一致。'
    '整個環境的空間幾何、地平線與光源方向保持合理一致。使用正確等距柱狀投影，保留兩極附近應有的拉伸；'
    '不要轉成普通透視、魚眼、裁切寬幅圖或小行星投影。細節清晰，避免拼接痕跡、物件重複或接縫突變。'
    '輸出單張完整全景，不加分格、邊框、文字、標誌或浮水印。',
)


class DirectorToolsAssetPrompt:
    @classmethod
    def INPUT_TYPES(cls):
        required = {
            'custom_prompt': ('STRING', {'default': '', 'multiline': True,
                                        'tooltip': 'Your character, scene or prop description. Preserved verbatim; no automatic translation.'}),
            'asset_type': (['Character', 'Panorama', GRID_MODE], {'default': 'Character'}),
            'language': (['English', '繁體中文'], {'default': 'English',
                                                'tooltip': 'Language of added preset text only. Custom prompt is not translated.'}),
            'character_layout': (LAYOUTS, {'default': 'Three views', 'tooltip': 'Character only. Front / side / back, optionally with a face close-up.'}),
        }
        for name, choices in OPTIONS.items():
            scope = ('Character / nine-grid character or prop. ' if name == 'background' else
                     'Character / nine-grid character. ' if name == 'expression' else
                     'Panorama / nine-grid scene. ' if name in ('environment', 'time_of_day') else
                     'Panorama / nine-grid scene or prop. ' if name == 'lighting' else '')
            required[name] = (list(choices), {'default': 'None', 'tooltip': scope + 'None adds no requirement; describe custom choices in custom_prompt.'})
        # Append the optional widget so existing workflow positions and API inputs remain valid.
        return {'required': required, 'optional': {
            'grid_asset_type': (GRID_ASSET_TYPES, {'default': 'Character',
                'tooltip': '九宮格資產 only: Character 角色 / Scene 場景 / Prop 道具. One 3x3 reference sheet of the same asset.'}),
            'aspect_ratio': (ASPECT_RATIOS, {'default': 'Auto',
                'tooltip': 'Width:height for the whole image. Character / nine-grid only. Auto: character unspecified, grid 1:1. Panorama always 2:1. Set actual generation dimensions separately.'}),
        }}

    RETURN_TYPES = ('STRING',)
    RETURN_NAMES = ('prompt',)
    FUNCTION = 'build_prompt'
    CATEGORY = 'image/Super Director Tools'
    DESCRIPTION = ('Assemble a character reference, seamless 2:1 panorama or 3x3 asset reference prompt. '
                   'No model calls or translation. Inactive mode options are ignored. '
                   'Set actual panorama width/height to 2:1 in your generation workflow.')

    def build_prompt(self, custom_prompt='', asset_type='Character', language='English',
                     character_layout='Three views', style='None', background='None', expression='None',
                     environment='None', time_of_day='None', lighting='None', grid_asset_type='Character', aspect_ratio='Auto'):
        if not isinstance(custom_prompt, str):
            raise ValueError('custom_prompt must be text.')
        if asset_type not in ('Character', 'Panorama', GRID_MODE):
            raise ValueError('asset_type must be Character, Panorama or ' + GRID_MODE + '.')
        if language not in ('English', '繁體中文'):
            raise ValueError('language must be English or 繁體中文.')
        if asset_type != 'Panorama' and aspect_ratio not in ASPECT_RATIOS:
            raise ValueError('aspect_ratio must be one of ' + ', '.join(ASPECT_RATIOS) + '.')
        index = 0 if language == 'English' else 1
        parts = [custom_prompt] if custom_prompt.strip() else []
        selected = {'style': style}
        if asset_type == 'Character':
            if character_layout not in LAYOUTS:
                raise ValueError('Unknown character_layout.')
            layout = 'Three views' if character_layout == 'Three views + face close-up' else character_layout
            parts.append(LAYOUT_PROMPTS[layout][index])
            if character_layout == 'Three views + face close-up':
                parts.append((
                    'Add one separate face close-up of the same character, preserving the exact facial identity and hairstyle.',
                    '另加一個同一角色的獨立臉部特寫，保持完全一致的五官身份與髮型。',
                )[index])
            parts.append(CHARACTER_CONSISTENCY[index])
            if aspect_ratio != 'Auto':
                parts.append((
                    f'Use a {aspect_ratio} width-to-height aspect ratio for the whole image. Compose all views to fit this canvas without cropping the figure.',
                    f'整張圖片的寬高比為 {aspect_ratio}，將所有視圖安排在此畫布內，不裁切人物。',
                )[index])
            selected.update(background=background, expression=expression)
        elif asset_type == 'Panorama':
            parts.append(PANORAMA_PROMPT[index])
            selected.update(environment=environment, time_of_day=time_of_day, lighting=lighting)
        else:
            parts.append(grid_asset_prompt(grid_asset_type, index, '1:1' if aspect_ratio == 'Auto' else aspect_ratio))
            if grid_asset_type == 'Character':
                selected.update(background=background, expression=expression)
            elif grid_asset_type == 'Scene':
                selected.update(environment=environment, time_of_day=time_of_day, lighting=lighting)
            else:
                selected.update(background=background, lighting=lighting)
        for name, value in selected.items():
            if not isinstance(value, str) or value not in OPTIONS[name]:
                raise ValueError(f'Unknown {name}: choose one of {", ".join(OPTIONS[name])}.')
            text = OPTIONS[name][value][index]
            if text:
                parts.append(text)
        return ('\n\n'.join(parts),)
