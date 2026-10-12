# Shot presets implementation plan

Goal: reusable shots from one panorama, with batch images and labeled overview.
Architecture: shared validated JSON contract; viewer UI writes canonical widgets;
new batch node reuses sample_panorama; sheet assembly is independent of projection.
Tech: Python/PyTorch/Pillow and browser ES modules, no new dependencies.

- [x] Add Python/JS tests for camera conversions and preset validation.
- [x] Implement matching conversion and versioned preset contract.
- [x] Add batch tests; implement batch render, contact sheet and sidecars.
- [x] Add browser coverage; implement preset UI and synced angular controls.
- [x] Register nodes, supply sample preset JSON and document usage.
- [x] Run regression suite and browser checks; review and fix findings.
