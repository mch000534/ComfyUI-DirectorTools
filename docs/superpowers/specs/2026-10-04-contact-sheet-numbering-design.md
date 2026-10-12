# Contact Sheet automatic labels

User requests replacing multiline labels with prefix text and a starting number.
Required inputs: images, columns, thumb_size, prefix (SH), start_number (1).
Generate sequential labels in batch order, minimum three numeric digits. Empty
prefix allows numbers alone. Numbers above 999 expand naturally; start permits 0.
Reject multiline/control-character prefixes, prefixes over 80 characters, and
non-integer or out-of-range starts (0..999999999). Reuse the existing sheet renderer.
Batch Panorama keeps its shot-ID captions unchanged. Existing Contact Sheet
workflow/API label inputs require migration, documented in README.
