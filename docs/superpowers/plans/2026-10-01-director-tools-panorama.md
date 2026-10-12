# Director Tools · Panorama viewer Implementation Plan

> Execute in the current isolated project directory; user authorized implementation in chat. Use test-driven-development and verification-before-completion. Review each task before progressing.

**Goal:** Deliver an installable single-node flat panorama camera with persistent framing.

**Architecture:** Pure crop geometry shared by contract between Python and JS; torch resampling on backend; standard ComfyUI execution metadata feeds a DOM canvas camera.

**Tech Stack:** Python standard library, existing ComfyUI torch/NumPy/Pillow; browser ES modules and Canvas; unittest and Node test runner.

## Tasks

- [x] Write geometry contract tests in tests/test_geometry.py and tests/geometry.test.mjs; run to observe missing-module failures. Implement geometry.py and web/lib/geometry.mjs; run both suites.
- [x] Write actual tensor node tests in tests/test_node.py; confirm missing-node failure. Implement nodes.py and __init__.py. Check identity, crop position, shapes, invalid inputs and bounded temporary preview metadata.
- [x] Write browser acceptance tests for drag, wheel, ratio sizes, restored widgets and cleanup. Implement web/lib/viewport.mjs and web/director_tools_panorama.js using current frontend hooks. Run Node and real browser tests.
- [x] Add example_workflows/director_tools_panorama.json, an API example and synthetic 2:1 panorama; README install/use/API caveats; LICENSE and pyproject.toml.
- [x] Verify in local ComfyUI if available without modifying user's existing installation. Record checks and known limitations; commit project; create clean install ZIP.

All production dependencies are supplied by ComfyUI. Test tooling stays outside the installation dependency list. No publishing or modifications to existing ComfyUI installations are required.
