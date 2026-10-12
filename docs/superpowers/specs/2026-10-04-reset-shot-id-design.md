# Reset Shot ID

Add a Reset Shot ID button in the viewer's preset actions. Renumber every saved
preset in existing list order as SH001, SH002, …, preserving all other fields.
Preserve selection by its index, update Shot ID and the JSON text, and persist
node properties so presets_json and Batch Panorama receive the new IDs.

The action changes identifiers only; camera settings and unsaved name/source
fields stay unchanged. Build and validate the next document before one graph
mutation. Existing exports/previously saved files remain historical snapshots.
With no presets set Shot ID to SH000 so the existing increment-before-add flow
creates SH001 on the next Add preset. Empty documents remain valid viewer state.

Keep input/output schemas and backend unchanged. Advance the frontend import
version to 0.8.2. Tests cover list order (rather than sorting by old IDs), immutable
source objects, all settings retained, selection and JSON synchronization, empty
reset followed by Add, unchanged camera and actual ComfyUI controls.
