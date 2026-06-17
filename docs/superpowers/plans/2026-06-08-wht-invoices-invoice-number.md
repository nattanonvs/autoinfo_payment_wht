# WHT Invoices Invoice Number Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a readonly “Invoice Number” column in `WHT Invoices` showing `account.move.name` while keeping the existing `invoice_id` column clickable.

**Architecture:** Store a computed `invoice_number` on `account.payment.invoice.line` derived from `invoice_id.name`, and render it as the first column in the WHT invoices tree view.

**Tech Stack:** Odoo 15 (Python ORM fields/compute), XML views (tree column ordering), Odoo test framework (`odoo.tests`).

---

## File Structure

**Modify**
- `C:\odoo\APPreadytouse\autoinfo_payment_wht\models\account_payment.py`
- `C:\odoo\APPreadytouse\autoinfo_payment_wht\views\account_payment_view.xml`

**Create**
- `C:\odoo\APPreadytouse\autoinfo_payment_wht\tests\__init__.py`
- `C:\odoo\APPreadytouse\autoinfo_payment_wht\tests\test_wht_invoice_number.py`

---

### Task 1: Add stored computed field `invoice_number`

**Files:**
- Modify: `C:\odoo\APPreadytouse\autoinfo_payment_wht\models\account_payment.py`

- [ ] **Step 1: Add failing test skeleton (will fail until field exists)**

Create `tests/test_wht_invoice_number.py`:

```python
from odoo.tests.common import TransactionCase


class TestWhtInvoiceNumber(TransactionCase):
    def test_invoice_number_is_from_invoice_name(self):
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": partner.id,
                "amount": 1.0,
            }
        )
        inv = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": partner.id,
                "invoice_date": "2026-06-08",
            }
        )
        inv.name = "BILL/TEST/0001"

        line = self.env["account.payment.invoice.line"].create(
            {"payment_id": payment.id, "invoice_id": inv.id}
        )

        self.assertEqual(line.invoice_number, "BILL/TEST/0001")
```

- [ ] **Step 2: Run test to verify it fails**

Run (example, adjust your odoo-bin path/config/db to your environment):

```bash
python3 /var/odoo/odoo15/odoo-bin -c /etc/odoo/odoo.conf -d <db_name> --test-enable --stop-after-init -i autoinfo_payment_wht
```

Expected: FAIL complaining `invoice_number` does not exist / AttributeError.

- [ ] **Step 3: Implement the field on `account.payment.invoice.line`**

In `models/account_payment.py`, inside `class AccountPaymentInvoiceLine(models.Model):` add:

```python
invoice_number = fields.Char(
    string="Invoice Number",
    compute="_compute_invoice_number",
    store=True,
    readonly=True,
)


@api.depends("invoice_id", "invoice_id.name")
def _compute_invoice_number(self):
    for line in self:
        line.invoice_number = line.invoice_id.name or ""
```

- [ ] **Step 4: Run tests again**

Run:

```bash
python3 /var/odoo/odoo15/odoo-bin -c /etc/odoo/odoo.conf -d <db_name> --test-enable --stop-after-init -u autoinfo_payment_wht
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add models/account_payment.py tests/test_wht_invoice_number.py tests/__init__.py
git commit -m "feat: add invoice_number on payment invoice lines"
```

---

### Task 2: Show “Invoice Number” column in WHT Invoices tree

**Files:**
- Modify: `C:\odoo\APPreadytouse\autoinfo_payment_wht\views\account_payment_view.xml`

- [ ] **Step 1: Update the tree columns**

In both inherited views (`inbound` and `vendor`) update the tree to:

```xml
<tree editable="bottom">
    <field name="invoice_number" readonly="1"/>
    <field name="invoice_id"/>
    <field name="amount_untaxed" readonly="1"/>
    <field name="base_amount"/>
    <field name="apply_wht"/>
</tree>
```

- [ ] **Step 2: Upgrade module and verify manually**

Run:

```bash
python3 /var/odoo/odoo15/odoo-bin -c /etc/odoo/odoo.conf -d <db_name> -u autoinfo_payment_wht --stop-after-init
```

Manual checks:
- Add invoices in the invoice selection tab (`processing_invoice_ids`).
- Open `WHT Invoices`:
  - `Invoice Number` column shows the invoice `name`
  - `Invoice` column is clickable and opens the correct invoice/bill

- [ ] **Step 3: Commit**

```bash
git add views/account_payment_view.xml
git commit -m "feat: show invoice number in WHT Invoices"
```

---

### Task 3: Guardrails and regression checks

**Files:**
- Modify: `C:\odoo\APPreadytouse\autoinfo_payment_wht\docs\usage_guide.md` (optional, only if you want to document the new column)

- [ ] **Step 1: Confirm no Windows paths appear in deliverable docs**

Run:

```bash
git grep -n "C:/\\|C:\\\\"
```

Expected: no output.

- [ ] **Step 2: Optional docs update**

Add one line in usage guide under WHT Invoices describing the new “Invoice Number” column.

- [ ] **Step 3: Final commit (if docs changed)**

```bash
git add docs/usage_guide.md
git commit -m "docs: mention invoice number column"
```

---

## Spec Coverage Self-Check
- Spec “Data Model Changes” → Task 1 adds stored computed `invoice_number`.
- Spec “View Changes” → Task 2 adds `invoice_number` as first column and keeps `invoice_id` clickable.
- Spec “Behavior / Data Flow” → Field depends on `invoice_id.name` so it updates when lines are generated.

