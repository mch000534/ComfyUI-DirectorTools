# Common shot names with custom entry

Replace the Shot name text field with a select containing Establishing, Extreme
wide, Wide, Full, Medium wide, Medium, Medium close-up, Close-up, Extreme
close-up, Over-the-shoulder, POV, Two-shot, Insert, Detail and Custom. Show Chinese
translations in option labels, keeping English names in existing JSON fields.
Default remains Wide.

Custom displays a separate labeled text field with the existing 80-character
limit. Switching to a common name hides the custom field, preserving its draft.
Loading a saved standard name selects it; all other saved names automatically
select Custom and restore the exact text. Add and Save read the active name
mode. The mode is UI state; serialized name remains a plain string and JSON,
backend, batch and output contracts remain unchanged. Names do not change the
camera. Frontend module version advances to 0.7.6.

Browser tests cover standard selection/save, conditional custom visibility,
custom name persistence/restoration, legacy custom names, control layout,
Add/Save, preset selection, import/export and unchanged camera interactions.
