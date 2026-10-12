# Registry automatic publishing

The agreed publishing flow is a push to `main` changing `pyproject.toml`, with
`REGISTRY_ACCESS_TOKEN` stored as a repository Actions secret. Add a manual
dispatch entry point for retries. Keep the current release at 0.10.3.

Use the official Comfy-Org publish action, pinned to a commit, after checking
the current project version against the Registry versions API. An already
registered version is skipped; API/network failures stop the job rather than
being treated as permission to publish. This also avoids publishing when only
metadata changes. Publishing to a non-main branch is disabled.

The workflow grants only repository contents read access, serializes publishing
runs without cancelling an in-progress upload, and checks for the secret before
publishing. `.comfyignore` already excludes `.github/` from the node archive.
Update the maintenance section of README.md with the automatic flow and how to
inspect the Actions result.

Validate workflow syntax and embedded scripts, confirm the GitHub secret name,
and manually run the deployed workflow against the existing 0.10.3 release.
That run must skip upload, with no new release or version bump. A future
unpublished version must take the official publishing path.
