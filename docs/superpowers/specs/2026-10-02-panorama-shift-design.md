# Panorama horizontal seam inspection

User requests a node to shift panorama horizontally, inspect the original left/right
join and output IMAGE plus an image-to-image seam repair prompt.

DirectorToolsPanoramaShift / Director Tools · Panorama Shift:
- image: floating IMAGE BHWC, 1/3/4 channels, supports source batches.
- shift_x: fraction of source width, -1 to 1, default 0.5; positive moves right.
- Round to nearest integer pixel, ties away from zero. Circular torch.roll on W.
- Preserve dimensions, dtype/device and pixels. No interpolation or image mutation.
- Append prompt STRING describing the exact original seam position after shifting.
- At zero/full-width shift the original seam stays across the outside edges; otherwise
  it is a vertical boundary at column offset % width. Odd widths round to a pixel.
- Prompt requests local join repair (geometry/texture/lighting) while preserving
  equirectangular projection, pole stretching, scene content and periodic outer edges.
  Lock both outer edge regions and copy all pixels outside the minimum interior repair
  strip unchanged from the shifted input. At the default half-roll, edit only the middle
  seam strip; use its untouched neighbors as reference. Do not regenerate the full image.
  If the join remains on the outside edges, request unchanged output instead of edge
  repair and recommend a separate half-roll pass for panoramas wider than one pixel.
  Prompt-only guidance is not pixel enforcement; strict preservation requires downstream
  masked inpainting and compositing the original shifted pixels outside the mask.
  Never apply the perspective-view refinement prompt to the full panorama.

Tests: default half-roll pixel order, negative shift/inverse, fractional rounding,
single-column and full turn behavior, batches/channels/dtype, invalid input rejection,
join-location prompt and unchanged input. Provide a UI/API example with PreviewAny
and SaveImage; test backend registration, actual downstream STRING and image pixels.
