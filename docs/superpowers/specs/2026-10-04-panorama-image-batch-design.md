# Batch Panorama emits a true IMAGE batch

The user requests a single IMAGE batch from Batch Panorama. Keep all ports,
inputs and preset schema, replacing the list output with concatenated tensors
[shot_count,H,W,3] and setting OUTPUT_IS_LIST to all false. Retain preset order,
input dtype/device, camera sampling, contact sheet, metadata and saved sidecars.

A tensor batch requires identical dimensions. Check all preset widths/heights
before sampling or writing files. Reject mixed dimensions with a message to
unify dimensions or use separate Batch Panorama nodes. Do not resize or pad
silently. Standalone viewer presets can still hold mixed sizes, but each Batch
Panorama invocation must use a uniform set.

Update bundled batch examples to uniform 640×360. Document the v0.8 migration
from list mapping to single batch execution, which also changes downstream node
execution from once per shot to once per batch.

Tests verify tensor type, shape, exact pixels/order/height, dtype/device,
metadata and sidecars, direct Contact Sheet consumption and pre-sampling failure
for both mixed ratios and mixed resolutions. Actual isolated ComfyUI verifies
registration, three Save Image results and one downstream Contact Sheet with
all three shots, plus the viewer presets_json connection.
