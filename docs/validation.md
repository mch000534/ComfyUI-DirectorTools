# v0.10.3 validation

Corrected scene-grid compass placement on 2026-10-04: top=north,
bottom=south, left=west, right=east. All 64 Python tests pass. The updated
regression first failed on the old east-facing top-center panel, then passed
after both English and Chinese panel lists and consistency instructions were
corrected. README and the current design document use the corrected layout.
This backend-only template change requires a ComfyUI restart and a new execution.

## v0.10.2 validation

Validated the fixed scene-grid layout on 2026-10-04. All 64 Python and 17
JavaScript tests pass. The new regression first failed on the missing top-left
position. It now verifies all nine row-major positions in both languages:
establishing / east / 45-degree downward oblique; west / orthographic plan /
north; focal-area medium / south / detail. It confirms a shared directional
camera anchor and removes the old all-nine-perspective requirement. The
existing 16:9 ratio remains present. README version and local links were checked.

This is a backend template change; no frontend behavior was modified and no
live browser run was repeated. Restart ComfyUI and execute again to refresh
the generated STRING. Image generation and visual adherence are not tested.

## v0.10.1 validation

Validated Asset Prompt aspect ratios on 2026-10-04. All 63 Python and 17
JavaScript unit tests pass. The new backend test failed before aspect_ratio
was accepted. Tests verify character ratios, both language templates, grid
whole-sheet and cell ratios, Auto grid 1:1, removal of square requirements for
16:9, Panorama fixed 2:1, invalid ratios, and every advertised dropdown option.
Frontend tests verify ratio visibility outside Panorama and preservation while
hidden. Actual ComfyUI browser checks preserve a saved 16:9 selection through
mode switches, API serialization and reload; a legacy ten-widget workflow
loads with aspect_ratio=Auto. The grid screenshot was visually inspected.

Old and new API examples and README links/version were verified. Generation
dimensions are not changed by this STRING-only node. Restart ComfyUI and
refresh to load the new optional widget and frontend version key.

## v0.10.0 validation

Validated nine-grid assets on 2026-10-04. All 62 Python and 17 JavaScript unit
tests pass. New backend tests cover Character / Scene / Prop in English and
Traditional Chinese, exactly nine numbered views, original multiline text,
mode-specific option isolation and invalid asset types. The new frontend test
checks immediate subtype switching and hidden value preservation. These tests
failed before the new mode and subtype callback were implemented.

The isolated ComfyUI browser test confirms all three grid asset types display
only the applicable fields, preserve values on workflow reload, serialize all
API inputs, and load a v0.9 workflow with its original ten widget positions and
the new subtype default. Both old and new API examples execute locally. The
asset-prompt-nine-grid.png screenshot was visually checked. No image generation
was queued; prompt assembly and UI behavior are verified, not model adherence
to grid geometry or cross-panel identity. Restart ComfyUI and refresh to load
the new backend mode and frontend cache key.

## v0.9.1 validation

Validated mode-specific Asset Prompt fields on 2026-10-04. All 60 Python and
16 JavaScript unit tests pass. Four new frontend tests verify initial field
visibility, immediate switching, shrinking hidden rows, value and widget
identity preservation, existing callbacks, idempotent installation and workflow
configure hooks. The tests failed before the controls module existed.

An isolated headless browser against a separate ComfyUI 0.38.2 / frontend 1.53.6
instance verifies both modes, workflow serialization and reload, switching back
without losing inactive values, and unchanged API inputs. No generation was
queued and the user's running workflow was not modified. The screenshot
asset-prompt-panorama.png was visually checked: only common and panorama
parameters are rendered, without empty rows. Save the workflow and refresh the
page to load the new frontend extension.

## v0.9.0 validation

Validated Asset Prompt on 2026-10-04. All 59 Python tests and 12 JavaScript
unit tests pass. Six new tests first failed because the node was not registered,
then passed after implementation. They cover the default English three-view
sheet, single full body, face close-up, Chinese character and panorama text,
2:1 equirectangular wraparound guidance, inactive mode isolation, original
multiline text preservation, invalid inputs and every advertised dropdown choice.

The new node uses native ComfyUI inputs and a single STRING output, without
frontend changes or external services. The registration and generation method
are exercised by package-level tests; a live ComfyUI execution was not run for
this version. Restart ComfyUI to load the new backend node. The existing PyTorch
environment emits a pynvml deprecation warning; the tests complete successfully.

## v0.8.2 validation

Validated Reset Shot ID on 2026-10-04. All 12 JavaScript unit tests pass; the
renumbering unit test failed before implementation. Browser fixture verifies
five saved shots become SH001–SH005 in list order, all non-ID fields remain
identical, current selection remains the fifth shot, Shot ID and JSON update,
and the camera values remain unchanged. Empty reset followed by Add starts
SH001. Existing import/export, naming, selection and camera interactions pass,
with WebGL maximum reference error 0.500/255.

A fresh isolated browser context against actual ComfyUI at port 8888 verifies
the same renumbered document, selected shot, ID field, JSON and unchanged camera.
No generation was queued and the user's workflow was not modified. This is a
frontend change: save the workflow and refresh the page to load the button.

## v0.8.1 validation

Validated aspect-aware contact sheet cells on 2026-10-04. All 53 Python tests
pass. Before implementation, regression assertions reproduced the oversized
square-cell dimensions for landscape/portrait images. After implementation,
three 16:9 images with thumb_size 187 and two columns produce 374×258 instead
of 374×422. White-pixel tests confirm populated image cells have no top/bottom
letterboxing. Portrait and square sizing, label bands and input preservation
also pass.

Actual isolated ComfyUI execution verifies three 640×360 batch shots remain
unchanged, the Batch Panorama contact sheet is now 768×168, and a downstream
Contact Sheet at thumb_size 64 outputs one 192×60 sheet. Metadata and sidecars
still pass. Both nodes use the shared implementation. Restart the backend and
run the workflow again to regenerate existing previews.

## v0.8.0 validation

Validated true Batch Panorama IMAGE output on 2026-10-04. All 52 Python tests
pass. The tensor/mixed-dimension tests failed against the old list implementation
and passed after the change. Coverage includes tensor [N,H,W,3], output-list
flags, exact independent reference pixels/order/height, dtype/device, unchanged
sidecars and metadata, direct Contact Sheet compatibility, and mixed-size
rejection before sampling or file creation.

Isolated ComfyUI 0.38.2 execution verifies output_is_list is all false, three
640×360 Save Image outputs, the existing 768×280 contact sheet, and one downstream
Contact Sheet consuming the complete batch and producing a 192×88 image. The
bundled batch examples now use a uniform size. The frontend viewer presets_json
connection also passes native queue execution with three images and one sheet.
Existing open ComfyUI instances
need a backend restart for this Python output contract change.

## v0.7.6 validation

Validated common Shot name selection and custom entry on 2026-10-04. The
browser regression failed against the old text input before implementation.
The fixture now passes default Wide, standard Close-up save, conditional custom
field visibility, legacy custom names, custom preset restoration and layout
bounds, alongside existing Add/Save, JSON, selection and preview tests. WebGL
maximum reference error remains 0.500/255. All 11 JS unit tests pass.

A fresh isolated browser context against actual ComfyUI at port 8888 verifies
Close-up persistence and hidden custom input, then saves the Chinese custom name
窗邊逆光, switches away/back and verifies Custom mode and the exact name.
No generation was queued and the user's workflow was not modified. Existing
open pages need to be refreshed after saving their workflow.

## v0.7.5 validation

Validated Add preset on 2026-10-04. All 11 JS unit tests pass, covering ID
increments, retained padding, digit expansion, case-insensitive collision skips,
blank/non-numeric suffixes and values beyond Number's safe integer range.
The new ID test failed before implementation and passed afterward.

Browser fixture passes with Apply preset absent, additions SH020 → SH021 →
SH022, occupied-ID skip to SH023, captured camera/dimensions/identification,
unchanged older presets and failed-add atomicity. Existing selection, preview,
JSON, camera interaction and cleanup tests pass; WebGL maximum reference error
remains 0.500/255. Camera round-trip assertions allow floating-point tolerance.

A fresh isolated browser context against the actual ComfyUI at port 8888 also
verified Apply is absent, Add appends one shot without replacing older shots,
and both selected preset and Shot ID field match the new ID. No generation was
queued and the user workflow was not modified.

## v0.7.4 validation

Reproduced the reported issue in the user's open Comfy Desktop page on
2026-10-04: selecting SH001 updated identification but left SH002 camera angles
and the old applied message. The running server served the updated source, but
the open page retained earlier event handlers. Restored the original selection
without refreshing or replacing the unsaved workflow.

Versioned the frontend module import chain and added input plus change handling.
Repeated events with unchanged camera values avoid a second graph mutation.
The input-only regression failed before the event fix and passed afterward.
Browser fixture checks immediate camera/dimension/height application, changed
preview pixels and unchanged saved presets; existing interactions still pass,
with WebGL maximum reference error 0.500/255. All 10 JS unit tests pass.
A fresh isolated browser context against the actual ComfyUI at port 8888 loaded
shot_controls.mjs?v=0.7.4 and switched two presets with camera/field assertions,
without clicking Apply or queuing generation. Existing open pages require a
refresh after saving their workflow.

## v0.7.3 validation

Validated automatic preset selection on 2026-10-04 with the browser fixture.
Switching between two saved shots immediately applies position, zoom, projection,
aspect ratio, dimensions and height, updates identification fields and changes
rendered preview pixels. Saved preset documents remain unchanged. Existing manual
Apply, JSON import/export, restore, legacy migration, pan/zoom, source replacement
and cleanup tests pass; WebGL reference comparison remains 0.500/255 maximum error.
Selection schedules only local redraw, never backend generation.

## v0.7.2 validation

Validated viewer presets_json on 2026-10-04: all 51 Python tests pass. Tests cover
append-only output slots, exact saved-document transfer, current-node selection,
empty presets, malformed documents and boolean schema rejection, plus direct
Batch Panorama consumption. The actual isolated ComfyUI frontend imports the
connected example, edits/saves a preset and submits through native queuePrompt.
Hidden workflow metadata reaches the viewer, its STRING reaches Batch Panorama,
and three shot images plus one contact sheet are produced. A PreviewAny consumer
confirms the latest saved yaw, not an older/default JSON. Existing image and prompt
slots stay at 0 and 1. Syntax, example JSON and package metadata pass.

## v0.7.1 validation

Validated Contact Sheet automatic numbering on 2026-10-04: all 49 Python tests
pass. Coverage includes the new prefix/start_number input contract, SH010-style
sequences, 999→1000 digit expansion, empty prefixes, zero start, invalid prefixes
and starts, and existing sheet pixel/input-preservation checks. Only Contact Sheet
label inputs changed; Batch Panorama shot-ID captions are unchanged. Legacy
multiline-label workflows/API inputs need the migration described in README.

## v0.7.0 validation

Validated Panorama Shift on 2026-10-02. All 48 Python tests pass, including
half-width and negative circular shifts, ties-away-from-zero rounding, inverse
restoration for odd/even widths, full-turn and single-column behavior, input
immutability, batch/1/3/4-channel handling, dtype/device preservation, malformed
inputs and accurate seam locations in the repair prompt.

Isolated ComfyUI 0.38.2 CPU API execution passed shifts 0.5, -0.25 and 1. Saved
PNG pixels exactly match independently calculated circular shifts of the source;
the built-in PreviewAny receives the STRING with correct original-join location.
Frontend 1.53.6 imports the supplied UI example, exposes IMAGE/STRING ports,
keeps both downstream connections and successfully executes SaveImage/PreviewAny.
Syntax, example JSON and package metadata checks pass. No dependencies changed.

This node reorders pixels, not a seam detector or AI repair model. Downstream
repair quality was not evaluated. CUDA/MPS and non-macOS platforms remain untested.
The temporary host used isolated input/output/user state and was stopped afterward.

```sh
COMFY_TEST_URL=http://127.0.0.1:8199 python tests/comfy-panorama-shift-smoke.py
COMFY_TEST_URL=http://127.0.0.1:8199 \
PLAYWRIGHT_MODULE=/absolute/path/to/playwright \
node tests/comfy-panorama-shift-browser.mjs
```

## v0.6.1 validation

Validated the appended Panorama viewer `prompt` STRING on 2026-10-02:
43 Python tests pass, including mode-specific enhancement instructions, simulated
height wording, and unchanged IMAGE output index and pixels. Isolated ComfyUI API
tests pass STRING propagation to the built-in PreviewAny node over four executions.
Real frontend testing imports a legacy single-output workflow and confirms the new
STRING port appears, original image links execute, presets restore and the batch
workflow still executes. The prompt is editing guidance; model repair quality was
not tested and the node does not apply AI enhancement itself.

## v0.6.0 validation

Validated additions on 2026-10-02 using an isolated ComfyUI instance, CPU and the
default frontend, with all test input/output/user state under `/private/tmp`.

- 41 Python tests pass, including angle round trips, malformed presets, case-insensitive
  ID uniqueness, filename/manifest collisions, aggregate pixel budget rejection before
  sampling, mixed-size shot ordering and pixels versus the existing panorama sampler,
  original-image preservation, label bands and paired PNG/JSON writes.
- 10 JavaScript tests pass, including camera conversion and shared preset validation.
- Browser fixture passes camera degree editing, invalid FOV recovery, save/apply,
  JSON text and file import, export download, atomic invalid import, workflow restore,
  legacy Flat migration, pan/zoom and WebGL reference pixel comparison (0.500/255 max).
- Real ComfyUI API execution passes list IMAGE propagation to Save Image: 640×360,
  640×360 and 360×640 shots, a 768×280 sheet, and matching metadata sidecars.
- Real ComfyUI frontend passes named preset save/apply, non-serialized auxiliary
  controls, workflow reload, original camera input preservation and batch example
  import/execution. Restored legacy node sizes expand to fit the new controls.
- Read-only peer review findings about sidecar naming collisions and malformed
  aspect ratio validation were reproduced, fixed and rechecked with no blockers.
- Python syntax, example JSON, package metadata and new-file whitespace pass.

The fixture is not a full ComfyUI host, so both fixture and host integration were
used. CUDA/MPS, Windows/Linux and experimental frontend renderers remain untested.
The existing host emits a PyTorch pynvml deprecation warning; dependencies were
not changed. CPU contact sheets and saved PNGs are 8-bit visualizations; original
shot IMAGE outputs retain tensor dtype/device. Source ID is a manual asset label,
not an automatic file locator or an identity check. No production host was restarted.

Reproduce the new integration check with a dedicated test server:

```sh
COMFY_TEST_URL=http://127.0.0.1:8199 \
COMFY_TEST_OUTPUT=/absolute/path/to/isolated/output \
python tests/comfy-shots-smoke.py
```

## Earlier v0.3.0 validation

Validated on 2026-10-01 with an isolated local ComfyUI instance. The user's existing custom_nodes, inputs, outputs and settings were not modified. Test data and host state lived in a separate workspace directory.

## Environment

- ComfyUI 0.38.1, source commit `20ca544e`
- comfyui-frontend-package 1.53.6
- Python 3.12.11, PyTorch 2.10.0.dev20250925
- macOS, CPU execution
- Node.js 22.22.3; headless Google Chrome through development-only Playwright

## Passed checks

- 24 Python unit tests: world-height ray intersection and inverse ray checks, height bounds and Flat compatibility, spherical rays/cardinal directions, periodic bilinear seam, perspective tensor versus independent scalar reference, pole and chunk handling, projection compatibility, geometry, ratios, integer dimension rounding, invalid settings, output tensor shape and dtype/device, coordinate ramp pixel values, identity crop, no input mutation, border handling, row chunk boundary, bounded source preview, node registration, explicit-run cache invalidation.
- 8 Node.js geometry tests: positive/negative height and zero-height compatibility, spherical UV, wrapped dragging and pitch limits, shared Python/JS crop fixtures, all ratio boundaries, dimension synchronization, drag direction and clamping.
- WebGL2 shader: five camera configurations including heights +0.8/-0.8 and tilted cameras on an NPOT texture against independent CPU bilinear sampling; maximum error 0.500/255.
- Browser fixture: seamless horizontal navigation, height changes preview pixels, height reset/restore, legacy six-widget migration to Flat and seven-widget migration preserving projection (both height=0), pointer drag, wheel isolation, reset, locked ratios, Free dimensions, serialized values, workflow restoration, disconnect, removal, and a new execution arriving during an active drag.
- Real ComfyUI API: registration, only one auto-loaded extension entry, 16:9 at 1920×1080, Free at 777×301 with height +0.8, 9:16 at 608×1080 with height -0.8, and a repeated identical prompt after deleting the preceding temporary preview. All runs succeeded and produced PNGs with exact requested dimensions and a fresh source preview reference.
- Real ComfyUI frontend: import the included example workflow, first-run source preview, drag and both wheel directions with unchanged ComfyUI graph scale, height +0.4 preview and correct `/prompt` inputs without the DOM widget leaking into inputs, save/reload with exactly identical framing and height inputs, and successful execution after reload.
- Python syntax, JavaScript syntax, JSON workflow and TOML metadata parsing; whitespace checks.
- Read-only peer review of world-up geometry, scalar/tensor/shader parity, validation, persistence and legacy migration found no blocking issues.

`preview.png` is a screenshot from the real ComfyUI frontend using the included synthetic 2:1 panorama.

## Implementation decisions verified against the host

V1 `INPUT_TYPES` nodes are supported by the current backend. Extension uses `WEB_DIRECTORY`, `registerExtension`, `beforeRegisterNodeDef`, `addDOMWidget`, `onExecuted`, `onConfigure` and connection/removal hooks. Helpers have `.mjs` extensions because the backend's `/extensions` scanner recursively lists `.js` files, including subdirectories; helpers are explicitly imported by the sole `.js` entry.

Each explicit run regenerates this node's output and temporary preview via `IS_CHANGED = NaN`. This prevents stale cached metadata from keeping a deleted preview unavailable. It leaves upstream execution caching intact. Source replacement first ends the active gesture and releases pointer capture, before clearing source metadata.

## Reproduce integration checks

Start an isolated ComfyUI server on port 8199, install this folder in its custom_nodes, and copy `example_workflows/test-panorama.png` to its input directory. These scripts load a sample workflow and save test images; use a dedicated test instance.

```sh
COMFY_TEST_URL=http://127.0.0.1:8199 \
COMFY_TEST_TEMP=/absolute/path/to/isolated/comfy/temp \
python tests/comfy-smoke.py

PLAYWRIGHT_MODULE=/absolute/path/to/playwright \
node tests/browser-smoke.mjs

COMFY_TEST_URL=http://127.0.0.1:8199 \
PLAYWRIGHT_MODULE=/absolute/path/to/playwright \
node tests/comfy-browser-smoke.mjs
```

`COMFY_TEST_TEMP` is optional; when supplied, the API test deletes only the preview filename returned by its previous run to verify recovery. The browser test writes a preview screenshot to `docs/preview.png`.

## Limits

CUDA/MPS execution, Windows/Linux, older frontends and the experimental Vue node renderer were not tested. CPU tensor paths and the default renderer on the versions above were tested. Existing host startup emits a `pynvml` deprecation warning from its installed PyTorch dependency; this project does not install or use pynvml directly.

Preview pixels are downsampled 8-bit source pixels; final output uses the original tensor. Spherical preview and final output use the same perspective ray and periodic bilinear sampling contract, including a normalized ray intersecting a unit sphere from origin (0,height,0). Downsampling and 8-bit preview quantization can produce differences from the original tensor output. Height simulates movement inside a textured sphere; there is no scene depth or true occlusion/parallax reconstruction. Batch-image handling is not implemented. WebGL2 is required for spherical preview; native context-loss recovery is implemented but not exercised by integration tests.
