## Configuration Guide — autoinfo_payment_wht (Odoo 15)

### Dependencies
- `dtr_payment_invoice` must be installed to use `processing_invoice_ids` on payment.
- `dtr_taxation` must be installed to use the Withholding Tax tab and fields `tax_id1/pay_amount1/wht_amount1`.

### Best Practices
- Use `WHT Invoices` as the source of truth for which invoices are included for WHT calculation.
- Avoid editing `pay_amount1` manually; it should be derived from selected invoices and WHT base amounts.

