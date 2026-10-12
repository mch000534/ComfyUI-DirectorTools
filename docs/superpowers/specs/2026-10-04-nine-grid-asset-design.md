# Nine-grid asset mode

使用者要求 Asset Prompt 新增「九宮格資產」，用於角色、場景、道具。新增模式值 Nine-grid asset · 九宮格資產，grid_asset_type 選單 Character / Scene / Prop，預設角色。輸出仍為單一 STRING，語言預設英文且可選繁體中文，自訂描述保留原文。

共用九格規則：一張正方形、等大 3×3 格子，由左至右、由上至下；同一資產多視圖與細節，無間隔、粗框、文字。角色安排六個全身視角與臉、手／配件、服裝細節；場景安排六個空間視角與主要區域、次要區域、細節；道具安排六面、前後四分之三與細節。每類別另要求身份、幾何或結構一致。

前端只顯示共用欄位、九宮格類別和該類別可用選項。角色使用 background / expression；場景使用 environment / time_of_day / lighting；道具使用 background / lighting。character_layout 不適用。切換不重設任何值。

新欄位放在 INPUT_TYPES.optional，排序於原有 required 欄位之後；保留舊 workflow 的 widget 值位置，舊 API 可不傳新欄位。新模板獨立於 grid_asset_prompt.py。升版 0.10.0，更新前端模組快取鍵、README 與 API 片段。

驗證兩種語言、三類資產、九格數量與順序、選項隔離、前端類別切換、保存載入與舊 API 片段。實際圖片生成尺寸在下游設 1:1，Grid Split 3×3 可拆圖；本節點不產生或驗證圖片。
