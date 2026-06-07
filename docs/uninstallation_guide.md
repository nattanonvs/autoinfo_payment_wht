## Uninstallation Guide — autoinfo_payment_wht (Odoo 15)

### Before Uninstall
- Ensure no critical workflow depends on the custom tabs `WHT Invoices` / `WHT Summary`.

### Temporary Disable (Recommended Method)
- Odoo has no true “disable” switch for a module.
- Recommended approach is to uninstall, then reinstall when needed.

### Uninstall (UI)
1. Apps → search `AutoInfo Payment WHT`
2. Click Uninstall

### Notes
- This module extends `account.payment` and adds a custom model `account.payment.invoice.line`.
- Uninstall will remove fields/views from the UI.
