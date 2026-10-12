# Camera Height Implementation Plan

**Goal:** Add persistent sphere-relative camera elevation with matching preview/output.

**Architecture:** Append one optional widget, share ray-sphere intersection across scalar Python/JS, tensor backend and native shader. Preserve zero-height and Flat behavior.

**Tech Stack:** Existing Python/PyTorch, JavaScript/WebGL2 and development-only browser tests.

## Chunk 1: Geometry and output
- [x] Write failing Python/JS elevation tests: center latitude equals .5-asin(h)/pi, world-height with pitch, unit intersection, zero compatibility and seam.
- [x] Run tests red, implement scalar geometry and tensor intersection; add node finite bound validation and optional slider after projection.
- [x] Verify tensor/reference sampling and old calls unchanged.

Files: geometry.py, nodes.py, web/lib/geometry.mjs, tests/test_panorama.py, tests/test_node.py, tests/panorama.test.mjs.

## Chunk 2: Preview and persistence
- [x] Extend shader GPU/CPU comparisons with heights ±.8; run red then add uniform and intersection.
- [x] Extend viewport settings/status/reset and extension callback; migrate legacy six/seven-widget workflows to height zero.
- [x] Browser fixture and real ComfyUI tests: height changes preview/output, serializes/reloads, reset zero, wheel isolation remains.

Files: web/lib/panorama_renderer.mjs, web/lib/viewport.mjs, web/lib/extension.mjs, tests/webgl.html, tests/viewport.html, tests/browser-smoke.mjs, tests/comfy-browser-smoke.mjs.

## Chunk 3: Delivery
- [x] Update README, example workflow/API, version and validation with geometric limits and actual evidence.
- [x] Run complete unit/browser/isolated host checks, read-only code review, resolve findings.
- [x] Commit and verify v0.3.0 ZIP; stop isolated host.
