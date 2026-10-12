# Asset Prompt Implementation Plan

**Goal:** 提供角色與全景生成提示詞組合節點。

**Architecture:** 獨立 Python 模組定義本地雙語模板與 INPUT_TYPES，註冊至既有 mappings。原生選單、單一 STRING 輸出，無前端客製與外部服務。

**Tech Stack:** Python、ComfyUI 原生節點 API、unittest。

- [x] 新增 tests/test_asset_prompt.py，先驗證節點未註冊造成失敗。
- [x] 新增 asset_prompt.py、註冊節點，驗證語言與模式的輸出隔離。
- [x] 更新版本、README 與 API 範例。
- [x] 執行完整 Python、JavaScript 測試，記錄結果。

本目錄無 Git，不建立提交；使用者已要求直接實作，直接完成並回報。
