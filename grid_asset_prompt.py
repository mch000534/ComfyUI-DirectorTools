"""Nine-panel reference-sheet templates, with row-major view plans."""

GRID_MODE = 'Nine-grid asset · 九宮格資產'
GRID_ASSET_TYPES = ['Character', 'Scene', 'Prop']

GRID_LAYOUT = (
    'Create one asset reference sheet in a strict 3x3 grid with exactly nine equal-sized panels. '
    'Read the panels left to right, top to bottom. Each panel has one distinct view of the same described asset, '
    'not nine unrelated designs or variations. Keep panel boundaries aligned, with no gutters, thick borders, '
    'overlapping views, text, captions, labels, logos or watermarks. Preserve a consistent visual style, '
    'color palette, materials and lighting across all nine panels. Keep the subject readable within each panel. '
    'Output one complete sheet, not nine separate files.',
    '製作一張資產參考設定圖，嚴格排列為 3×3 九宮格，包含恰好九個等大的格子。'
    '由左至右、由上至下閱讀，每格呈現同一個指定資產的一種不同視圖，不是九個無關設計或變體。'
    '格子邊界整齊對齊，不加間隔、粗邊框、跨格重疊、文字、說明、標籤、標誌或浮水印。'
    '九格保持一致的畫風、色調、材質與光線，每格主體清晰可辨。輸出一張完整設定圖，不是九個獨立檔案。',
)

GRID_VIEWS = {
    'Character': (
        ['front full-body view', 'left profile full-body view', 'right profile full-body view',
         'back full-body view', 'front three-quarter full-body view', 'rear three-quarter full-body view',
         'face close-up', 'hands and accessories detail', 'costume and material detail'],
        ['正面全身', '左側全身', '右側全身', '背面全身', '正面四分之三全身', '背面四分之三全身',
         '臉部特寫', '手部與配件細節', '服裝與材質細節'],
    ),
    'Scene': (
        ['top-left: wide establishing view of the entire location',
         'top-center: directional perspective view looking north',
         'top-right: elevated oblique view looking downward at a 45-degree angle',
         'middle-left: directional perspective view looking west',
         'center: orthographic top-down floor plan or site plan of the same location',
         'middle-right: directional perspective view looking east',
         'bottom-left: main focal area medium view',
         'bottom-center: directional perspective view looking south',
         'bottom-right: environmental detail close-up'],
        ['左上：整個場景的全景建立視角',
         '上中：朝北的方位透視視圖',
         '右上：向下俯視 45 度的斜角視圖',
         '左中：朝西的方位透視視圖',
         '正中央：同一場景的正投影頂視平面圖／場地平面圖',
         '右中：朝東的方位透視視圖',
         '左下：主要焦點區域中景',
         '下中：朝南的方位透視視圖',
         '右下：環境細節特寫'],
    ),
    'Prop': (
        ['front view', 'back view', 'left side view', 'right side view', 'top view', 'bottom view',
         'front three-quarter view', 'rear three-quarter view', 'material and construction detail close-up'],
        ['正面', '背面', '左側', '右側', '頂面', '底面', '正面四分之三視角', '背面四分之三視角',
         '材質與結構細節特寫'],
    ),
}

GRID_CONSISTENCY = {
    'Character': (
        'All panels depict the same character. Preserve facial features, hairstyle, anatomy, body proportions, '
        'costume, colors and accessories. Keep full-body panels at a consistent scale and neutral standing pose, '
        'showing the entire figure from head to feet; detail panels may use a closer scale.',
        '所有格子呈現同一角色，維持五官、髮型、人體結構、身體比例、服裝、顏色與配件一致。'
        '全身格使用相同比例與自然站姿，完整顯示頭至腳；細節格可放大呈現。',
    ),
    'Scene': (
        'All panels depict the same location from spatially consistent camera positions and directions. '
        'Preserve the layout, geometry, relative object positions, structures, landmarks, materials, time of day '
        'and lighting direction. Do not redesign the location or invent different rooms between panels. '
        'The center panel is a true orthographic plan seen vertically from above, without perspective convergence, '
        'not a tilted aerial photograph. Orient the plan with north up and east right. For an interior, reveal the '
        'floor layout without the ceiling obscuring it; for an exterior, show the site layout. '
        'Use the same camera anchor, height and field of view for the four directional panels, rotating only '
        'toward their stated compass directions. Their grid positions are top=north, bottom=south, left=west, '
        'right=east. Match all landmarks and relative positions to the central plan. The other eight panels '
        'use perspective projection. The 45-degree panel is an elevated downward-looking oblique view. '
        'Do not add compass labels, arrows, measurement text or captions.',
        '所有格子呈現同一場景，攝影機位置與方向符合一致的空間關係。'
        '保留佈局、幾何、物件相對位置、結構、地標、材質、時間及光源方向。'
        '不要在不同格子重新設計地點或變成不同房間。'
        '中央格必須是垂直向下看的真正正投影平面圖，沒有透視收斂，不是傾斜空拍照片。'
        '平面圖以北朝上、東朝右；室內移除天花板遮擋以顯示地面佈局，室外顯示場地佈局。'
        '四個方位視圖使用同一攝影機基準位置、高度與視野，僅轉向指定方位；格子位置為上北、下南、左西、右東。'
        '各視圖地標與相對位置必須對應中央平面圖。其餘八格使用透視投影，45 度格為由高處向下看的俯視斜角。'
        '不要加方位文字、箭頭、尺寸文字或圖說。',
    ),
    'Prop': (
        'All panels depict the same prop. Preserve its exact shape, dimensions, proportions, materials, '
        'colors, wear patterns, components and construction across views. Keep the complete prop visible in '
        'the eight overview panels at a consistent scale; use the ninth panel for a close-up. '
        'Do not create alternate prop designs or add components between views.',
        '所有格子呈現同一道具，維持形狀、尺寸、比例、材質、顏色、磨損、零件與結構一致。'
        '前八格以相同比例完整顯示道具，第九格呈現細節特寫。不要生成不同款式或在不同視圖增加零件。',
    ),
}


def grid_asset_prompt(asset, language_index, aspect_ratio='1:1'):
    if asset not in GRID_ASSET_TYPES:
        raise ValueError('grid_asset_type must be Character, Scene or Prop.')
    heading = ('Panel order:', '九格順序：')[language_index]
    views = '\n'.join(f'{i}. {view}' for i, view in enumerate(GRID_VIEWS[asset][language_index], 1))
    ratio = (
        f'Use a {aspect_ratio} width-to-height aspect ratio for the whole sheet and for each of its nine equal-sized panels.',
        f'整張設定圖與九個等大格子的寬高比皆為 {aspect_ratio}。',
    )[language_index]
    if aspect_ratio == '1:1':
        ratio += (' The sheet and every panel are square.', ' 整張設定圖與每格皆為正方形。')[language_index]
    return '\n\n'.join([GRID_LAYOUT[language_index], ratio, heading + '\n' + views, GRID_CONSISTENCY[asset][language_index]])
