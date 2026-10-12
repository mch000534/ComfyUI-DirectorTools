# Contact sheet cells follow thumbnail proportions

The user reports excessive top/bottom letterboxing caused by square thumbnail
cells. Shared contact_sheet rendering will size cells to the actual thumbnail
bounds while preserving aspect ratio, content and a separate 24-pixel ID band.
thumb_size remains the maximum/longest thumbnail edge, 64–512 pixels.

Compute each thumbnail's fitted dimensions, then derive cell width and height
from the maximum fitted bounds. Batch Panorama and Contact Sheet accept uniform
image dimensions, so populated cells have no added letterboxing. The unused
cells in a partial final row remain background. Keep output slots, batch pixels,
metadata, sidecars, order and labels unchanged.

For the user's 16:9 example at thumb_size 187 with 2 columns and 3 shots, each
image is 187×105 with a 24-pixel label band. Output changes 374×422 → 374×258.
Landscape and portrait cells both shrink their short dimension; square inputs
retain the prior geometry.

Tests check exact landscape/portrait/square sheet sizes, white content reaching
all populated-cell edges, label-band separation, input preservation and shared
rendering. Integration checks Batch Panorama and downstream Contact Sheet sizes.
