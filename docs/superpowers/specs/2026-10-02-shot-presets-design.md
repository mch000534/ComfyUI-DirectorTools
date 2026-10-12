# Shot presets, camera angles and batch framing

Approved scope: the first three recommendations in this chat. Extend the existing
viewer without changing its backend input order or projection. Keep canonical
center_x, center_y and zoom; expose degree controls as synchronized UI controls.
Vertical FOV is 2*atan(tan(37.5 degrees)/zoom), zoom 1–32, pitch ±89.9 degrees.

Store a versioned JSON document in node properties: schema_version=1, shots array.
Each shot has shot_id, name, source_id, yaw, pitch, vertical_fov, width, height,
aspect_ratio, camera_height. One document refers to one panorama; source_id is a
user-supplied asset label, not an automatic image loader or camera position.
Save, replace, select/apply, delete, import and export presets inside the viewer.
Invalid import must leave current state unchanged. Presets persist in workflows.

Batch Panorama consumes that JSON and one IMAGE, renders shots in document order,
outputs an IMAGE list (mixed dimensions allowed), a labeled contact sheet and JSON.
Contact sheet thumbnails preserve aspect ratio and never put labels on shot images.
Limit to 64 shots, validate dimensions and aggregate pixel budgets before rendering.
Optional save_files writes each PNG and same-name JSON with unique safe filenames
under ComfyUI output; default off. Metadata cannot supply filesystem paths.
Expose a separate Contact Sheet node for uniform IMAGE batches such as Grid Split.

Test degree/zoom parity in Python and JS, JSON round trips and rejection, batch
pixels versus existing sampler, list ordering/mixed sizes, sheet label separation,
file sidecars, legacy viewer restore and native browser save/import/apply controls.
No new installation dependencies. This folder is not a Git checkout.
