# Director Tools · Panorama viewer v0.2 panorama360 design

Approved in chat on 2026-10-01: 360-degree spherical preview and matching perspective IMAGE output, following the behavior of ProGamerGov/ComfyUI_preview360panorama. Horizontal longitude wraps at the source seam; this is not just tiling a flat crop.

## Architecture and compatibility

Keep a single DirectorToolsPanoramaViewer node, with existing aspect, width, height, normalized centers and zoom widgets. Append an optional `projection` combo: `360 Panorama` (new UI node default) and `Flat`. Legacy API payloads without projection keep Flat via the Python default. Frontend recognizes old six-value workflows and explicitly selects Flat on restore, preserving saved framing. New examples select 360 Panorama.

Center_x denotes source longitude: 0 and 1 both point to the left/right seam, .5 points to the middle. Center_y maps source latitude, .5 at the equator; camera pitch clamps to ±89.9 degrees. Zoom=1 gives a 75-degree vertical FOV; zoom scales focal length, keeping horizontal FOV derived from actual output aspect. Drag right moves the visible image right (camera longitude decreases), drag down tilts the camera up. Wrap longitude modulo 1, never clamp it horizontally. Fixed viewport, dimension synchronization, workflow save, source preview lifecycle and explicit-run regeneration remain.

## Projection contract

For each output pixel center, form a perspective ray `(x*tan(vfov/2)*aspect, -y*tan(vfov/2), 1)` and normalize it. Rotate it by camera pitch and longitude, obtain spherical longitude with atan2 and latitude with asin, then map to equirectangular UV. Bilinear source sampling wraps U and clamps V. Both WebGL shader and PyTorch use identical axis signs, FOV and pixel-center conventions. CPU reference UV fixtures test both implementations.

WebGL2 preview uses original small preview texture, explicit texel-fetch bilinear sampling with longitude wrapping (including non-power-of-two textures), and source-origin convention top-left. A shader renders only when camera or size changes; no continuous animation. ComfyUI owns an overlay 2D canvas for border/thirds and interaction over the preview canvas. WebGL resources are released on removal, recreated after context loss; unavailable WebGL reports an actionable preview status rather than showing misleading flat imagery. Backend retains full tensor precision and row-chunked grids.

No code or Three.js library is copied from the reference. Functional behavior is a reference; new implementation uses browser and existing ComfyUI dependencies. Preview and output geometry match, while texture resolution and browser/backend interpolation can differ.

## Verification

Tests first: shared spherical UV fixtures, cardinal views, vertical signs, FOV/zoom/aspect, periodic horizontal seam bilinear samples, no black border, matching browser shader vs independent CPU samples, drag past seam repeatedly, workflow restoration and legacy migration. Run real isolated ComfyUI and package updated ZIP. Document CPU/default-renderer validation and GPU/legacy-browser limits.

Reference: https://github.com/ProGamerGov/ComfyUI_preview360panorama/blob/main/js/pano_viewer.js (perspective camera, equirectangular scene background, mouse longitude/latitude, wheel FOV).
