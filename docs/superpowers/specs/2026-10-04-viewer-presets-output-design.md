# Viewer presets JSON output

Append presets_json STRING at slot 2, keeping IMAGE/prompt slots 0/1 stable.
Use hidden UNIQUE_ID and EXTRA_PNGINFO to retrieve this node's director_tools_shots
property from the submitted workflow. Validate with the existing preset contract.
Missing/empty saved presets return schema_version 1 and an empty shots array;
Batch Panorama's existing validation rejects an empty list. Never silently invent
a shot from the current framing. No visible input widgets or frontend state changes.
Document API metadata and wire an example branching the original source IMAGE to
viewer and batch, with the viewer's slot 2 feeding batch presets_json.
Verify saved-presets identity, exact transfer, malformed-state rejection and actual
frontend submission/execution, especially edits saved immediately before queuing.
