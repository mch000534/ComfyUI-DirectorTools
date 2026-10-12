# Panorama shift implementation plan

Goal: make panorama boundary defects visible and send a local repair instruction.
Architecture: isolated panorama_shift.py uses torch.roll; registration appends a node.
Tech: existing Python/PyTorch. No new dependencies or frontend extension.

- [x] Write/run failing tests for roll pixels, round trips, validation and prompts.
- [x] Implement shift node and register it without altering existing nodes.
- [x] Add documentation and UI/API sample with IMAGE and STRING consumers.
- [x] Verify regression suite and actual isolated ComfyUI execution.
