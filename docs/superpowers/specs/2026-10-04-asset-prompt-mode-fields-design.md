# Asset Prompt mode fields

依使用者要求，原先「所有欄位可見」改為共用欄位與所選模式欄位。共用：custom_prompt、asset_type、language、style；角色：character_layout、background、expression；全景：environment、time_of_day、lighting。

新增獨立前端 extension，僅安裝到 DirectorToolsAssetPrompt；建立節點、選單 callback 與 onConfigure 後同步 hidden / options.hidden / computeSize。保留 widget 身份、順序、type、value 與 serializeValue，隱藏列不占高度，切換回來恢復原有屬性。替換 widgets 陣列以同步 Nodes 2.0 的渲染快照。

不更改 Python 輸入格式、API、模板或其他節點；workflow 保留兩模式所有值。測試預設、即時切換、原有 callback、載入和保存的數值完整性，以及真實 ComfyUI 的序列化。
