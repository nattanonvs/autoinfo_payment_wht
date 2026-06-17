## Design — WHT Invoices: Show Invoice Number (Odoo 15)

### Context
- The `WHT Invoices` tab displays lines derived from invoices selected in `processing_invoice_ids`.
- Requirement: when invoice lines appear in `WHT Invoices`, show the invoice “number” that matches the invoice shown in the invoice tab.
- Confirmed by user: use the invoice number from `account.move.name`.
- UI requirement: show both:
  - Invoice Number (readonly text)
  - Invoice (many2one, clickable)

### Goals
- Each line in `WHT Invoices` shows a stable invoice number value (from `invoice_id.name`).
- Keep `invoice_id` clickable so users can open the invoice/bill.
- Update automatically when invoice lines are generated/updated from `processing_invoice_ids`.

### Non-Goals
- No changes to `account.move` name_get / global invoice display behavior.
- No changes to the `processing_invoice_ids` selection flow itself.

### Data Model Changes
- Model: `account.payment.invoice.line`
- Add field:
  - `invoice_number` (Char)
    - compute: from `invoice_id.name`
    - store: True
    - readonly: True
    - dependency: `invoice_id`, `invoice_id.name`

### View Changes
- Form views inheriting `dtr_taxation` payment forms:
  - `WHT Invoices` tree: add a first column `invoice_number` (readonly)
  - Keep existing column `invoice_id` so the record remains clickable

### Behavior / Data Flow
- When users add invoices into `processing_invoice_ids`, module generates `invoice_line_ids`.
- Each line already has `invoice_id`; `invoice_number` is derived from it.
- When invoice number changes on the invoice (rare), stored compute keeps the line updated.

### Edge Cases
- If `invoice_id` is empty, `invoice_number` should be empty.
- Multi-company: derive number directly from the invoice record; no extra company logic needed.

### Testing / Verification (Manual)
1. Open payment, add 1–2 invoices in `processing_invoice_ids`.
2. Open `WHT Invoices` tab and confirm:
   - `Invoice Number` is populated and equals invoice `name`
   - `Invoice` column remains clickable and opens the correct invoice
3. Add another invoice, confirm new line shows its number immediately.

