# Butopêa Practical Test 

This repository is the submission for the Butopêa practical test for an Odoo 16 Backend Developer position. It contains three custom addons built and debugged inside a Docker-based Odoo 16 environment.

---

## Project Structure

```
odoo-dev/
├── addons/
│   ├── estate/            # Task foundation - real estate management module
│   ├── estate_account/    # Task A - invoice creation on property sale
│   └── course_catalog/    # Task B - broken module with 5 bugs to fix
├── docker-compose.yml
└── NOTES.md               # Workflow log: prompts used, bugs found, decisions made
```

---

## Setup and Running

**Prerequisites:** Docker and Docker Compose installed.

```bash
# Clone the repository
git clone <repo-url>
cd odoo-dev

# Start Odoo 16 and PostgreSQL
docker compose up
```

Odoo will be available at `http://localhost:8069`.

On first launch, create a new database through the web interface. Enable **demo data** if you want pre-populated partners and products for testing.

To stop the containers:

```bash
docker compose down
```

Data is persisted in named Docker volumes (`postgres_data`, `odoo_data`) and survives restarts.

---

## Addons

### `estate`

A real estate management module built following the official Odoo 16 tutorial. Provides:

- `estate.property` - listings with fields for price, state, area, orientation, and availability
- `estate.property.type` - categories (apartment, house, etc.)
- `estate.property.tag` - free-form labels
- `estate.property.offer` - buyer offers with accept/refuse actions and state transitions
- Kanban and list views, computed fields (best offer, total area), Python constraints, and a `sold`/`cancelled` state machine

### `estate_account`

Extends `estate` with accounting integration. Depends on both `estate` and Odoo's `account` module (Invoicing app must be installed). When a property is marked as sold:

- A draft customer invoice is automatically created for the buyer
- Invoice lines: 6% commission on the selling price + 100 fixed administrative fee
- A smart button on the property form shows the linked invoice count and opens the invoice list

The invoice is linked to the property via a `property_id` field on `account.move`, using a `One2many` relation to avoid cross-contamination with unrelated invoices.

### `course_catalog`

A small course management module provided in a broken state as Task B. Contains models for courses and enrollments with a computed `total_revenue` field. Five bugs were identified and fixed:

1. Invalid model name `res.user` corrected to `res.users`
2. Typo `model_course_catlog` in the ACL CSV corrected to `model_course_catalog`
3. Typo `instuctor_id` in the view XML corrected to `instructor_id`
4. `@api.depends("enrollment_ids")` corrected to `@api.depends("enrollment_ids.amount")` so revenue recomputes on amount changes
5. Missing required `name` attribute on a menu item causing an install-time constraint violation

---

## Installing the Modules

With the containers running and a database created, install modules using `docker exec`:

```bash
# Install the base estate module first
docker exec odoo16 odoo -c /etc/odoo/odoo.conf -d <your-database> -i estate --no-http --stop-after-init

# Install estate_account (requires Invoicing app already installed via UI)
docker exec odoo16 odoo -c /etc/odoo/odoo.conf -d <your-database> -i estate_account --no-http --stop-after-init

# Install course_catalog
docker exec odoo16 odoo -c /etc/odoo/odoo.conf -d <your-database> -i course_catalog --no-http --stop-after-init
```

Replace `<your-database>` with the name of the database you created (visible in Settings > Manage Databases).

> **Note:** `estate_account` requires the **Invoicing** app to be installed first. Install it from Apps in the Odoo UI before running the command above.

Alternatively, all modules can be installed through the Odoo UI via **Settings > Apps > Update Apps List**, then searching for each module by name.

---

## Task A - Acceptance Criteria Test

Open an Odoo shell session:

```bash
docker exec -it odoo16 odoo shell -c /etc/odoo/odoo.conf -d <your-database>
```

Then run the following in the shell to verify the invoice created on sale:

```python
# Find a sold property with invoices (e.g. one sold after estate_account was installed)
prop = env['estate.property'].search([
    ('state', '=', 'sold'),
    ('invoice_ids', '!=', False),
], limit=1)

invoice = prop.invoice_ids[0]

results = {
    'invoice_count == 1':       prop.invoice_count == 1,
    'move_type == out_invoice': invoice.move_type == 'out_invoice',
    'partner_id == buyer_id':   invoice.partner_id == prop.buyer_id,
    'amount_untaxed correct':   invoice.amount_untaxed == round(prop.selling_price * 0.06 + 100, 2),
    'state == draft':           invoice.state == 'draft',
}

for check, passed in results.items():
    print(f"{'PASS' if passed else 'FAIL'}  {check}")

print()
print('ALL PASSED:', all(results.values()))
```

Expected output when all criteria are met:

```
PASS  invoice_count == 1
PASS  move_type == out_invoice
PASS  partner_id == buyer_id
PASS  amount_untaxed correct
PASS  state == draft

ALL PASSED: True
```
