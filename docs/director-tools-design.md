# Director Tools Grid Split — v0.4.1

Extend the existing Director Tools · Panorama viewer package with one independent backend node;
retain its existing node ID, web extension and Panorama implementation.

Inputs: IMAGE (floating BHWC, 1/3/4 channels), integer rows/cols (1–64),
shot_number (1–rows*cols), optional separator_px (0–4096, default 0). Require rows <= height, cols <= width and a nonempty
batch. Row-major shot numbering starts at one.

Internal gaps only; no outside border removal, no automatic detection.
Content dimensions: cw = width - (cols-1)*separator_px,
ch = height - (rows-1)*separator_px. Require cw >= cols and ch >= rows.
Column i starts at floor(i*cw/cols) + i*separator_px and ends at
floor((i+1)*cw/cols) + i*separator_px (exclusive); rows analogously.
All content pixels occur exactly once; excluded bands have exactly separator_px
pixels. Cells differ by at most one pixel. With separator_px=0 the formulas
reduce to v0.4.0 behavior, including the default Python call signature.
selected_image is the exact crop, without interpolation or padding.
all_cells uses edge replication on the right/bottom to ceil(cw/cols) ×
ceil(ch/rows), permitting a dense IMAGE batch without removing source pixels.
Batch order: all shots from source 0, then all shots from source 1, etc.
selected_index = shot_number - 1, local to each source grid.

Validate both UI ranges and runtime arguments (including connected INT inputs).
Keep dtype/device; do not mutate source. Test nine-shot ordering, reconstruction
for nondivisible sizes, batch order, one-cell identity, registration and invalid inputs.
