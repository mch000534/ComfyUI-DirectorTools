# Director Tools · Panorama viewer v0.1 design

Approved in chat on 2026-10-01. One IMAGE input, one IMAGE output. Flat crop, no spherical projection or horizontal wrapping. A fixed aspect viewport contains a draggable image; zoom >= 1 covers the viewport without black borders.

## Contract

Inputs, in serialization order: image, aspect_ratio, width, height, center_x, center_y, zoom. Ratio presets: 16:9, 9:16, 1:1, 4:3, 3:2, 2.39:1, Free. Centers are normalized source coordinates. Presets synchronize dimensions in UI; backend rejects materially mismatched dimensions (one pixel rounding tolerance). Free uses width/height as its aspect. A single image is required; reject batches to avoid silently discarding frames.

The largest rectangle of the target aspect inside the source is the zoom=1 field of view. Divide its dimensions by zoom. Clamp the requested center so the rectangle stays inside the source. Both browser and Python use the same floating-point crop geometry. Backend samples output pixel centers with PyTorch bilinear grid sampling, align_corners=False and border padding. Source resolution and output resolution are independent.

## Preview lifecycle

Node is an output node so it can run without a downstream saver. Execution returns a bounded source preview through ComfyUI's standard temporary image/view mechanism in custom UI metadata, alongside the cropped IMAGE. First run acquires source; browser interactions subsequently run locally. Rerun produces final output. Changing upstream image/link invalidates the visible preview on graph edits; source-changing values upstream require another run. Workflow persists numeric inputs, not embedded source pixels. Restoring a workflow restores framing; run again if temporary preview is missing. Saved preview metadata is accepted through onExecuted/onConfigure. Each explicit execution regenerates this node output and temporary source preview using IS_CHANGED = NaN; upstream caches remain available. Replacing the source ends any active drag before clearing geometry metadata.

## Structure and dependencies

__init__.py registers one V1 node and WEB_DIRECTORY. geometry.py is standard-library crop math. nodes.py handles IMAGE validation, sampling and preview. web/director_tools_panorama.js uses registerExtension and addDOMWidget; web/lib holds reusable geometry/UI helpers (nested modules are not extension entry points). No bundled frontend or external packages. torch, NumPy, Pillow are existing ComfyUI dependencies.

## Validation

Python geometry and actual tensor tests: ratios, borders, extreme zoom, invalid dimensions/NaN, single-image enforcement, color ramps and output dimensions. Node built-in JS tests: geometry parity, size synchronization, UI lifecycle/workflow values. Browser smoke test with a real DOM and a small ComfyUI host fixture; real ComfyUI smoke run if locally available. Document exact tested host versions and limits.

## References checked 2026-10-01

- https://docs.comfy.org/custom-nodes/backend/server_overview (V1 remains supported)
- https://docs.comfy.org/custom-nodes/backend/images_and_masks (BHWC IMAGE)
- https://docs.comfy.org/custom-nodes/js/javascript_hooks
- https://github.com/Comfy-Org/ComfyUI/blob/master/nodes.py (temporary image conventions)
- https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/scripts/domWidget.ts (DOM widget API)
