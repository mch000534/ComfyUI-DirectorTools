# Add preset and automatic shot numbering

The user requests removal of Apply preset and addition of Add preset, which
captures the current camera and increments Shot ID automatically. Selection
continues to apply immediately. Save preset remains for replacing an existing
shot or saving an explicitly entered ID.

Add increments the numeric suffix of the entered ID, retaining its prefix and
padding (SH010 → SH011; SH999 → SH1000). Occupied IDs are skipped with the same
case-insensitive uniqueness rule as preset validation. An ID without a numeric
suffix gains 001; blank starts SH001. BigInt prevents large numeric suffixes
from losing precision.

The current source, name, camera, dimensions, aspect and height are captured.
Validate the complete next document before modifying properties or form fields.
On success append, persist, select the new shot, and update the Shot ID field.
On failure preserve the document and input ID. Existing JSON schema, backend
ports and Batch Panorama remain unchanged. Versioned imports advance to 0.7.5.

Verification covers sequential additions, padding, overflow, occupied IDs,
case-insensitive conflicts, exact large suffixes, camera capture, unchanged
existing shots, invalid-add atomicity, absence of Apply, selection and preview.
