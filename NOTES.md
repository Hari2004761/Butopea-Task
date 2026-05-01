# Butopêa Practical Test - Notes

## Workflow Description

All tasks completed using Claude Code as the primary AI tool, with Odoo 16 documentation and error tracebacks used to verify and correct AI output.

## Foundation

**Prompt 1:**
"I need to build an Odoo 16 custom addon called estate following the official Odoo tutorial. Create the basic module structure inside the addons folder with __manifest__.py and __init__.py files."

Observation: Created correct base structure with proper manifest format.

**Prompt 2:**
"Create the estate.property model with all fields required by the Odoo 16 tutorial including name, description, postcode, date_availability, expected_price, selling_price, bedrooms, living_area, facades, garage, garden, garden_area, garden_orientation, active, state."

Observation: All fields created with correct Odoo 16 field types.

**Prompt 3:**
"Complete the Foundation section - security file, additional models (property type, tag, offer), computed fields, constraints, kanban view, action buttons and state transitions."

Observation: Built all 4 models, views, state machine and buttons.

**Bug 1 - Odoo 17 vs 16 syntax (list vs tree):**
During installation, Odoo threw a ValueError on ir.ui.view.type: 'list'. I read the error traceback, identified it was a view type issue, and checked the Odoo 16 documentation which confirmed that list views use the <tree> tag in v16 - <list> was introduced in v17.

**Prompt 4:**
"There's a bug in estate_property_views.xml - Odoo 16 uses <tree> not <list> for list views. Please find and replace all instances across all view XML files."

Observation: Fixed 6 instances across 3 files and also fixed view_mode="list,form" to view_mode="tree,form" in the action record.

## Task A - estate_account

**Prompt 5:**
"Create a new Odoo 16 addon called estate_account inside the addons folder. It should depend on estate and account modules. When a property's action_sold is called, automatically create a draft customer invoice for the buyer_id with two invoice lines: 6% commission of selling_price and a fixed 100.00 administrative fee. Add a smart button showing invoice count. Do not modify the estate module to depend on account."

Observation: Created correct addon structure with _inherit pattern.

**Bug 2 - Missing buyer_id field:**
Claude Code initially used offer partner lookup instead of buyer_id because estate.property didn't have a buyer_id field. Fixed by adding buyer_id as Many2one to res.partner, setting it on offer acceptance and clearing on refusal. estate_account updated to read buyer_id directly.

**Bug 3 - Many2many instead of One2many for invoice_ids:**
invoice_ids was defined as Many2many which caused it to link to all existing invoices in the system. Fixed by adding a property_id field on account.move and computing invoice_ids as a One2many filtered by that field.

**Bug 4 - estate_account not loading:**
Module wasn't being called because Invoicing app wasn't installed. Installed Invoicing app which provides account.move model that estate_account depends on.

**Idempotency decision:**
Added guard in action_sold - if property is already sold or already has invoices, raise UserError instead of creating duplicate invoice. Documented as deliberate design choice.

**Acceptance criteria verification:**
Ran full test in Odoo shell:
- invoice_count == 1 ✅
- move_type == 'out_invoice' ✅
- partner_id == Azure Interior ✅
- amount_untaxed == 12100.0 (200000 * 0.06 + 100) ✅
- state == 'draft' ✅

ALL PASSED: True

## Task B - course_catalog

**Bug 1:** models/course.py line 11 - `res.user` is not a valid Odoo model, corrected to `res.users`.

**Bug 2:** security/ir.model.access.csv line 2 - `model_course_catlog` typo corrected to `model_course_catalog`.

**Bug 3:** views/course_views.xml line 16 - `instuctor_id` typo corrected to `instructor_id`.

**Bug 4:** models/course.py line 39 - `@api.depends("enrollment_ids")` corrected to `@api.depends("enrollment_ids.amount")` so total_revenue recomputes when enrollment amounts change.

**Bug 5:** views/course_views.xml line 82 - menu item missing required `name` attribute causing constraint violation on install.

Verified: module installs cleanly, form view renders without warnings, Total Revenue updates correctly when enrollments change (tested: 5000 + 2000 = 7000 shown correctly).

## Known Issues / Incomplete Items

- Missing license key in estate manifest (warning only, not blocking)
- estate_property_offer create method not overriding in batch (performance warning, not functional)
- Smart button on property form is hidden when invoice_count == 0. Properties sold before estate_account was installed show no button as no invoices exist for them. Intentional UX decision.