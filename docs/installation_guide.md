## Installation Guide — autoinfo_payment_wht (Odoo 15)

### Prerequisites
- Odoo 15
- Dependencies
  - account
  - dtr_taxation
  - dtr_payment_invoice

### Install (Localhost / Windows)
1. Copy module folder `autoinfo_payment_wht` into an addons path directory
   - Recommended base path: `C:\odoo\APPreadytouse\autoinfo_payment_wht`
2. Ensure `addons_path` contains `C:\odoo\APPreadytouse`
3. Restart Odoo (if running as service) or start `odoo-bin`
4. In Odoo UI:
   - Apps → Update Apps List
   - Search: `AutoInfo Payment WHT`
   - Install

### Install (Command Line)
Example:
- `python odoo-bin -c C:\odoo\odoo-15.0\odoo.conf -d <db_name> -i autoinfo_payment_wht --stop-after-init`

