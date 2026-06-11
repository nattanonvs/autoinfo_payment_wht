## Installation Guide — autoinfo_payment_wht (Odoo 15)

### Prerequisites
- Odoo 15
- Dependencies
  - account
  - dtr_taxation
  - dtr_payment_invoice
- Linux user with permission to deploy custom addons and restart Odoo service

### Install (Linux Server)
1. Copy module folder `autoinfo_payment_wht` into an addons path directory
   - Recommended base path: `/var/odoo/custom15_autoinfo/autoinfo_payment_wht`
2. Ensure `addons_path` contains `/var/odoo/custom15_autoinfo`
3. Ensure folder ownership and permissions are correct for the Odoo service user
   - Example: `chown -R odoo:odoo /var/odoo/custom15_autoinfo/autoinfo_payment_wht`
4. Confirm `odoo.conf` contains the custom addons path
   - Example: `addons_path = /var/odoo/odoo15/addons,/var/odoo/custom15_autoinfo`
5. Restart Odoo service or run module installation from command line
   - Example service restart: `systemctl restart odoo`
6. In Odoo UI:
   - Apps → Update Apps List
   - Search: `AutoInfo Payment WHT`
   - Install

### Install (Command Line)
Example:
- `python3 /var/odoo/odoo15/odoo-bin -c /etc/odoo/odoo.conf -d <db_name> -i autoinfo_payment_wht --stop-after-init`

### Post-Install Verification
- Open a payment that uses `processing_invoice_ids`
- Confirm tabs `WHT Invoices` and `WHT Summary` are visible
- Select a WHT type and verify `pay_amount1` / `wht_amount1` update from selected invoice lines
