# Registry Automatic Publishing Implementation Plan

> **For agentic workers:** Use subagent-driven-development to implement this plan.

**Goal:** Automatically publish new Registry versions after a main branch version update.

**Architecture:** A single GitHub Actions workflow checks Registry versions, then delegates uploads to the official pinned Comfy action. Existing versions skip upload. A manual run verifies installation without creating another release.

**Tech Stack:** GitHub Actions YAML, Python standard library, official Comfy publish action.

## Chunk 1: Workflow and documentation

### Task 1: Configure publishing

**Files:**
- Create `.github/workflows/publish_registry.yml`.
- Update the Registry maintenance section of `README.md`.

- [ ] Add `push` on main for `pyproject.toml`, plus `workflow_dispatch`.
- [ ] Pin checkout and official publish actions; use read-only contents permissions and concurrency without cancellation.
- [ ] Read the project name/version using Python and check the Registry versions API. Only a confirmed 404 or a successful version list missing the current version allows publish; other errors fail closed.
- [ ] Check a nonempty `REGISTRY_ACCESS_TOKEN` before the publish path. Pass it through the official action input.
- [ ] Skip an existing version. Do not change version 0.10.3 or manually publish another release.
- [ ] Document the automatic version update flow, secret location, manual entry point and skip behavior.
- [ ] Validate YAML and GitHub Actions semantics using actionlint, exercise the version check with existing/missing versions and API failure, and run `git diff --check`.
- [ ] Commit and push the reviewed workflow, then run it manually and verify the existing-version skip on GitHub.

No new unit-test files are needed for this configuration change; validate the actual workflow and run its embedded version-check script with controlled API responses.
