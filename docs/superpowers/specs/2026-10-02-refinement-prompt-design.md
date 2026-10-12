# Panorama viewer refinement prompt

User requests one prompt text output for downstream image-to-image enhancement
and spherical/wide-angle distortion correction. Append STRING prompt after IMAGE,
preserving image index 0, all inputs and all existing image sampling behavior.
Use English scene-preserving editing instructions, with mode-specific wording:
360 mode addresses residual spherical warping; simulated height adds off-center
correction; Flat only corrects visible lens distortion. Preserve perspective
convergence, curved objects, framing, lighting, identities and scene layout.
This is instruction generation, not automatic image processing or guaranteed repair.

Tests: append-output contract, both mode variants and simulated-height wording,
existing image regression suite, backend output registration and frontend workflow
restoration with old image links and a new STRING output slot.
