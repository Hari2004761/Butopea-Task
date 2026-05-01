ompt 1:
"I need to build an Odoo 16 custom addon called estate following the official Odoo tutorial. Create the basic module structure inside the addons folder with manifest.py and init.py files."
Observation: Created correct base structure with proper manifest format.
Prompt 2:
"Create the estate.property model with all fields required by the Odoo 16 tutorial..."
Observation: All fields created with correct types.
Prompt 3:
"Complete the entire Foundation section in one prompt — security file, additional models..."
Observation: Built all 4 models, views, state machine and buttons in one shot.
Prompt 4 (bug fix):
"There's a bug in estate_property_views.xml — Odoo 16 uses <tree> not <list> for list views. Please find and replace all instances..."
Observation: Claude Code used Odoo 17 syntax. Caught this from the error message and fixed it