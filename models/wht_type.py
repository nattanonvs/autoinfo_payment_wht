from odoo import models, fields

class WHTType(models.Model):
    _name = "wht.type"
    _description = "Withholding Tax Type"

    name = fields.Char(required=True)
    percent = fields.Float(string="Percent (%)", required=True)
    account_id = fields.Many2one(
        "account.account",
        string="WHT Payable Account",
        required=True,
    )
