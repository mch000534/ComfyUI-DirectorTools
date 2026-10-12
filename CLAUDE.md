# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

ComfyUI 自訂節點套件，提供 360° 全景取景、批次鏡頭預設與聯絡表功能。安裝方式為直接放入 `custom_nodes/` 目錄，**不可**用 `pip install .` 安裝。

## 測試指令

```sh
# Python 後端測試（需在 ComfyUI 的 Python 環境執行）
python -m unittest discover -s tests -p 'test_*.py'

# 只跑純幾何測試（一般 Python 即可，無 ComfyUI 依賴）
python -m unittest discover -s tests -p 'test_geometry.py'

# JavaScript 幾何測試（需 Node.js 18+，無 npm 安裝依賴）
npm test

# 瀏覽器 smoke test（需自行提供 Playwright）
PLAYWRIGHT_MODULE=/absolute/path/to/playwright node tests/browser-smoke.mjs
```

## 架構

### Python 後端

- `__init__.py`：節點註冊（`NODE_CLASS_MAPPINGS`、`NODE_DISPLAY_NAME_MAPPINGS`、`WEB_DIRECTORY`）
- `geometry.py`：**純 Python** 鏡頭投影與取景幾何，無框架依賴，與 `web/lib/geometry.mjs` 鏡像對應，兩者必須保持一致
- `nodes.py`：`DirectorToolsPanoramaViewer`，IMAGE 驗證、球面（`sample_panorama`）／平面（`sample_crop`）取樣、暫存 source preview
- `director_tools.py`：`DirectorToolsGridSplit`，格線切分節點
- `shot_nodes.py`：`DirectorToolsBatchPanorama` 與 `DirectorToolsContactSheet`，批次取景與聯絡表
- `refinement_prompt.py`：根據投影模式與視點高度產生圖生圖修復提示詞字串

### JavaScript 前端

- `web/director_tools_panorama.js`：前端 extension 入口，由 ComfyUI 的 `WEB_DIRECTORY` 載入
- `web/lib/extension.mjs`：節點 hooks（`beforeRegisterNodeDef`、`registerExtension`）、widgets 與 workflow 生命週期；清理時必須釋放事件與 observer
- `web/lib/viewport.mjs`：預覽 DOM widget、拖曳、滾輪、鍵盤操作
- `web/lib/panorama_renderer.mjs`：原生 WebGL2 球面透視預覽（自製，非 Three.js）
- `web/lib/geometry.mjs`：前端鏡頭幾何與尺寸同步（與 `geometry.py` 鏡像）
- `web/lib/presets.mjs`：命名鏡頭預設的 CRUD、JSON 匯入匯出
- `web/lib/shot_controls.mjs`：Yaw／Pitch／FOV 控制 widget

### 關鍵設計約束

1. **geometry.py 與 geometry.mjs 必須鏡像**：兩者的投影公式（`camera_angles`、球面 UV 計算）須完全一致，確保後端輸出與 WebGL 預覽一致。
2. **IMAGE tensor 格式**：ComfyUI 標準的 `[B, H, W, C]` float，`sample_panorama`／`sample_crop` 保留輸入的 dtype 與 device。
3. **接縫處理**：球面取樣在 U 方向包裹，透過左右各補一列再做 `grid_sample` 實現雙線性接縫取樣。
4. **預覽為縮圖**：節點內預覽最多 1536px，儲存在 ComfyUI 暫存；正式輸出直接使用輸入 tensor。
5. **無外部依賴**：只使用 ComfyUI 已附帶的 PyTorch、NumPy、Pillow；前端無 npm 套件。

## ComfyUI 節點 API 重點

- 後端節點繼承慣例（`INPUT_TYPES`、`RETURN_TYPES`、`FUNCTION`、`CATEGORY`）遵循 [官方 Python 節點 API](https://docs.comfy.org/custom-nodes/backend/server_overview)
- 前端使用 `registerExtension` + `beforeRegisterNodeDef` + `addDOMWidget`；修改時務必在 `onRemoved` 釋放所有事件監聽與 MutationObserver
- `WEB_DIRECTORY = './web'` 讓 ComfyUI 自動提供靜態 JS 檔案

## 不需要的東西

- 不需要 `pip install .`、不需要 Node.js 建置步驟
- Registry 發布使用 `pyproject.toml` 中的 `mch000534` Publisher 與 `comfy node publish`；`.comfyignore` 排除開發檔案。API Key 不可提交到 Git。
- 測試中的 ComfyUI smoke tests（`tests/comfy-*.py`）需要實際跑起來的 ComfyUI 實例
