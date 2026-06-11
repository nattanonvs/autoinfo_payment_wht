## Update Guide — autoinfo_payment_wht (Odoo 15)

### Update (Upgrade)
- Apps → search `AutoInfo Payment WHT` → Upgrade
- If Odoo runs as a service, restart service after code deployment
- Example: `systemctl restart odoo`

### Update (Command Line)
- `python3 /var/odoo/odoo15/odoo-bin -c /etc/odoo/odoo.conf -d <db_name> -u autoinfo_payment_wht --stop-after-init`

### Recommended Update Flow (Linux)
1. Deploy latest source to `/var/odoo/custom15_autoinfo/autoinfo_payment_wht`
2. Verify ownership and permissions for the Odoo service user
3. Restart Odoo service: `systemctl restart odoo`
4. Run upgrade command if needed
5. Validate payment form behavior in a test database before production rollout

### Timeline & Change Log

#### 15.0.1.1.0
- 2026-06-07
- Standardized module structure for Linux deployments under `/var/odoo/custom15_autoinfo`
- Added full documentation set under `docs/`
- Updated owner/author and credits

#### 15.0.1.0.1
- 2026-06-07
- Improved WHT calculation workflow:
  - Select invoices from `processing_invoice_ids`
  - Allow selecting subset invoices and editing WHT base per invoice
  - Sync with dtr_taxation fields (`tax_id1/pay_amount1/wht_amount1`)
- Fixed view inheritance issues and security access
