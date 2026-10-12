# Director Tools v0.5.0 validation — 2026-10-01

- Full Python suite: 35 passed (11 Grid Split tests plus original camera / panorama tests).
- JavaScript regression suite: 8 passed.
- Python 3.14 / PyTorch 2.14.1 on CPU.
- Separator tests check exact exclusion of 2px internal horizontal/vertical bands,
  multiple sources, nondivisible dimensions, edge padding, single-axis grids,
  one-cell identity, separator=0 / omitted compatibility, invalid types/ranges,
  and rejection when separator leaves empty cells.
- Existing test harness preloads torch.distributed.tensor before patch.dict restores
  sys.modules to avoid lazy-import operator re-registration in newer PyTorch.
- No live ComfyUI UI/server execution performed for this update.
- Uses optional input and default Python argument to preserve old workflow/API calls.

- Full naming update: package/folder, class and node ID, extension, preview message keys, CSS, workflows, tests and documentation renamed together.
- Rename verification: 35 Python tests and 8 JavaScript tests passed; all example JSON parsed.
