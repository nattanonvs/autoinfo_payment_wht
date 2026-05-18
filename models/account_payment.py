from odoo import models, fields, api


class AccountPaymentInvoiceLine(models.Model):
    _name = "account.payment.invoice.line"
    _description = "Payment Invoice Line"

    payment_id = fields.Many2one("account.payment", ondelete="cascade")
    invoice_id = fields.Many2one("account.move", string="Invoice")
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount",
        related="invoice_id.amount_untaxed",
        store=True,
    )
    base_amount = fields.Monetary(
        string="WHT Base Amount",
        currency_field="currency_id",
    )
    apply_wht = fields.Boolean(string="Apply WHT?")
    currency_id = fields.Many2one(
        related="payment_id.currency_id",
        store=True,
        readonly=True,
    )

    @api.onchange("invoice_id")
    def _onchange_invoice_id_set_base_amount(self):
        for line in self:
            if not line.invoice_id:
                continue
            base = line.invoice_id.amount_untaxed
            if line.payment_id and line.payment_id.currency_id:
                inv_currency = line.invoice_id.currency_id
                pay_currency = line.payment_id.currency_id
                company = line.payment_id.company_id
                date = line.payment_id.date or fields.Date.context_today(line)
                if inv_currency and pay_currency and inv_currency != pay_currency:
                    base = inv_currency._convert(base, pay_currency, company, date)
            line.base_amount = base


class AccountPayment(models.Model):
    _inherit = "account.payment"

    x_amount = fields.Monetary(currency_field="currency_id")

    invoice_line_ids = fields.One2many(
        "account.payment.invoice.line",
        "payment_id",
        string="Invoices for WHT",
    )

    wht_net_received = fields.Monetary(
        string="Net Received",
        currency_field="currency_id",
        compute="_compute_wht_net_received",
        store=True,
        readonly=True,
    )

    def _get_wht_base_total(self):
        self.ensure_one()
        selected = self.invoice_line_ids.filtered(lambda l: l.apply_wht)
        base = 0.0
        for line in selected:
            line_base = line.base_amount
            if not line_base and line.invoice_id:
                line_base = line.invoice_id.amount_untaxed
                inv_currency = line.invoice_id.currency_id
                pay_currency = self.currency_id
                company = self.company_id
                date = self.date or fields.Date.context_today(self)
                if inv_currency and pay_currency and inv_currency != pay_currency:
                    line_base = inv_currency._convert(line_base, pay_currency, company, date)
            base += line_base
        return base

    def _compute_wht_amount_from_base(self, base):
        self.ensure_one()
        if not self.tax_id1 or not base:
            return 0.0
        tax_res = self.tax_id1.compute_all(
            base,
            currency=self.currency_id,
            quantity=1.0,
            product=False,
            partner=self.partner_id,
        )
        return abs(sum(t.get("amount", 0.0) for t in tax_res.get("taxes", [])))

    @api.onchange("processing_invoice_ids")
    def _onchange_invoice_ids_load_lines(self):
        """โหลด invoice ที่เลือกใน payment มาใส่ตาราง invoice_line_ids อัตโนมัติ (Odoo 15 ใช้ invoice_ids)"""
        for payment in self:
            existing = {l.invoice_id.id: l for l in payment.invoice_line_ids if l.invoice_id}
            commands = [(5, 0, 0)]
            for inv in payment.processing_invoice_ids:
                if inv.id in existing:
                    commands.append(
                        (
                            0,
                            0,
                            {
                                "invoice_id": inv.id,
                                "apply_wht": existing[inv.id].apply_wht,
                                "base_amount": existing[inv.id].base_amount,
                            },
                        )
                    )
                    continue
                base = inv.amount_untaxed
                inv_currency = inv.currency_id
                pay_currency = payment.currency_id
                company = payment.company_id
                date = payment.date or fields.Date.context_today(payment)
                if inv_currency and pay_currency and inv_currency != pay_currency:
                    base = inv_currency._convert(base, pay_currency, company, date)
                commands.append(
                    (
                        0,
                        0,
                        {
                            "invoice_id": inv.id,
                            "apply_wht": True,
                            "base_amount": base,
                        },
                    )
                )
            payment.invoice_line_ids = commands
            payment._onchange_invoice_line_ids_sync_wht_fields()

    @api.onchange("tax_id1")
    def _onchange_tax_id1_auto_apply_lines(self):
        for payment in self:
            if not payment.tax_id1:
                continue
            if not payment.invoice_line_ids:
                continue
            if payment.invoice_line_ids.filtered(lambda l: l.apply_wht):
                continue
            for line in payment.invoice_line_ids:
                if not line.base_amount and line.invoice_id:
                    base = line.invoice_id.amount_untaxed
                    inv_currency = line.invoice_id.currency_id
                    pay_currency = payment.currency_id
                    company = payment.company_id
                    date = payment.date or fields.Date.context_today(payment)
                    if inv_currency and pay_currency and inv_currency != pay_currency:
                        base = inv_currency._convert(base, pay_currency, company, date)
                    line.base_amount = base
                if line.base_amount:
                    line.apply_wht = True

    @api.onchange("tax_id1")
    def _onchange_tax_id1(self):
        res = super()._onchange_tax_id1()
        self._onchange_tax_id1_auto_apply_lines()
        self._onchange_invoice_line_ids_sync_wht_fields()
        return res

    @api.onchange("invoice_line_ids", "tax_id1")
    def _onchange_invoice_line_ids_sync_wht_fields(self):
        for payment in self:
            if payment.tax_id1 and payment.invoice_line_ids and not payment.invoice_line_ids.filtered(lambda l: l.apply_wht):
                for line in payment.invoice_line_ids:
                    if line.base_amount:
                        line.apply_wht = True

            base = payment._get_wht_base_total()
            payment.pay_amount1 = base
            payment.wht_amount1 = payment._compute_wht_amount_from_base(base)

    @api.depends("pay_amount1", "wht_amount1")
    def _compute_wht_net_received(self):
        for payment in self:
            payment.wht_net_received = payment.pay_amount1 - payment.wht_amount1

    def _update_wht_fields_from_invoices(self):
        for payment in self:
            if payment.tax_id1 and payment.invoice_line_ids and not payment.invoice_line_ids.filtered(lambda l: l.apply_wht):
                payment.invoice_line_ids.filtered(lambda l: l.base_amount).write({"apply_wht": True})
            base = payment._get_wht_base_total()
            payment.write(
                {
                    "pay_amount1": base,
                    "wht_amount1": payment._compute_wht_amount_from_base(base),
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.filtered(lambda r: r.tax_id1 and r.invoice_line_ids)._update_wht_fields_from_invoices()
        return records

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get("auto_payment_wht_skip_sync"):
            return res
        if {"invoice_line_ids", "processing_invoice_ids", "tax_id1"} & set(vals.keys()):
            self.with_context(auto_payment_wht_skip_sync=True)._update_wht_fields_from_invoices()
        return res
