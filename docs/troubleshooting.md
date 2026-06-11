## Troubleshooting — autoinfo_payment_wht (Odoo 15)

### Linux Deployment Checklist
- Confirm module path is `/var/odoo/custom15_autoinfo/autoinfo_payment_wht`
- Confirm `addons_path` includes `/var/odoo/custom15_autoinfo`
- Confirm Odoo service has read access to the module directory
- Restart service after code deployment: `systemctl restart odoo`

### 1) Error: `<tax> amount is not valid`
Cause:
- dtr_taxation requires `pay_amount1` and `wht_amount1` to be non-zero when `tax_id1` is set.

Fix:
- Ensure at least one invoice is ticked in `WHT Invoices` (`Apply WHT?`)
- Ensure `WHT Base Amount` is not 0
- Re-check `tax_id1` and verify totals in `WHT Summary`

### 2) WHT amount does not update immediately
Checklist:
- Change `Apply WHT?` or `WHT Base Amount`, then re-check `tax_id1` value.
- If code was just deployed, make sure the latest module version is upgraded in the database.

### Credits

Development Team: The Auto-Info Co., Ltd. : Dev Team / Mr. Nattanon Vinyangkoon – Project conception, implementation, and thorough review of all deliverables.
AI Coding Assistant: TRAE SOLO / MICROSOFT 365 COPILOT - Utilized to support code generation and productivity improvements under human oversight (e.g., suggesting code snippets and optimizations).
