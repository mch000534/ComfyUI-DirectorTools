# Asset Prompt

新增 Director Tools · Asset Prompt，使用一般 ComfyUI 選單與多行描述，輸出一個 STRING prompt。無模型、翻譯服務或額外依賴。使用者已確認語言可選、預設英文；角色預設三視圖，也提供三視圖加臉部特寫與單張全身。

共用欄位：custom_prompt、asset_type、language、style。角色欄位：character_layout、background、expression；Panorama 欄位：environment、time_of_day、lighting。v0.9.1 起只顯示共用與當前模式的欄位，隱藏欄位的值保持不變；原生 widgets 支援 UI、API 與 workflow 儲存，非當前模式的選項不加入文字。選項可留 None，不主動覆蓋使用者描述。自訂描述保留原文，不宣稱自動翻譯。

角色提示詞要求人物一致、完整身體；三視圖的左右排列為正面、側面、背面；特寫使用同一人物。Panorama 要求 360×180°、等距柱狀投影、2:1、左右水平環繞銜接、接縫結構與曝光一致，保留投影在兩極的合理拉伸。提示詞是生成意圖，並非接縫品質保證或實際尺寸設定。

測試節點註冊、預設角色、單張與特寫、兩種語言、模式隔離、選項與自訂多行原文保留、錯誤參數。新增 README 使用說明與 API 範例，版本升到 0.9.0；既有前端模組未修改，維持原快取版本。
