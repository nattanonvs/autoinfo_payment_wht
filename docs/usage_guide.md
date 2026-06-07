## Usage Guide — autoinfo_payment_wht (Odoo 15)

### User Level: Basic
1. Open Payments (Receive/Send Money)
2. Select invoices from `processing_invoice_ids`
3. Go to tab `WHT Invoices`
   - Tick `Apply WHT?` for invoices to be included
   - Adjust `WHT Base Amount` (base before VAT) if needed
4. Go to tab `Withholding Tax` (from dtr_taxation)
   - Select `ภาษีหัก ณ ที่จ่าย` in `tax_id1`
   - `pay_amount1` and `wht_amount1` will update from selected invoices
5. Go to tab `WHT Summary` to review totals

### User Level: Intermediate
- Use `Apply WHT?` to include only invoices that you actually pay in this payment.
- Use `WHT Base Amount` to adjust base per invoice when partial base needs to be withheld.

### User Level: Admin
- Install/upgrade the module and verify dependencies are installed.
- Verify access rights for accounting users.

