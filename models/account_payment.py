from odoo import models, fields, api


class AccountPaymentInvoiceLine(models.Model):
    _name = "account.payment.invoice.line"
    _description = "Payment Invoice Line"

    payment_id = fields.Many2one("account.payment", ondelete="cascade")
    invoice_id = fields.Many2one("account.move", string="Invoice")
    invoice_number = fields.Char(
        compute="_compute_invoice_number",
        store=True,
        readonly=True,
    )
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

    @api.depends("invoice_id.name")
    def _compute_invoice_number(self):
        for line in self:
            line.invoice_number = line.invoice_id.name or False

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

    def _compute_wht_amount_from_base(self, base, tax=None, currency=None, partner=None):
        tax = tax or (self.tax_id1 if self else False)
        currency = currency or (self.currency_id if self else False)
        partner = partner or (self.partner_id if self else False)
        if not tax or not base:
            return 0.0
        tax_res = tax.compute_all(
            base,
            currency=currency,
            quantity=1.0,
            product=False,
            partner=partner,
        )
        return abs(sum(t.get("amount", 0.0) for t in tax_res.get("taxes", [])))

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
        if (not base) and (not selected) and self.processing_invoice_ids:
            currency = self.currency_id
            company = self.company_id
            date = self.date or fields.Date.context_today(self)
            for inv in self.processing_invoice_ids:
                line_base = inv.amount_untaxed
                inv_currency = inv.currency_id
                if inv_currency and currency and inv_currency != currency:
                    line_base = inv_currency._convert(line_base, currency, company, date)
                base += line_base
        return base

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

    def _get_m2m_ids_from_commands(self, commands, existing):
        ids = list(existing)
        for cmd in commands:
            op = cmd[0]
            if op == 6:
                ids = list(cmd[2] or [])
            elif op == 4:
                if cmd[1] not in ids:
                    ids.append(cmd[1])
            elif op == 3:
                if cmd[1] in ids:
                    ids.remove(cmd[1])
            elif op == 5:
                ids = []
        return ids

    def _get_invoice_line_dicts_after_commands(self, commands):
        self.ensure_one()
        current = [
            {
                "id": l.id,
                "invoice_id": l.invoice_id.id,
                "base_amount": l.base_amount,
                "apply_wht": l.apply_wht,
            }
            for l in self.invoice_line_ids
        ]
        by_id = {d["id"]: d for d in current if d["id"]}
        for cmd in commands:
            op = cmd[0]
            if op == 5:
                current = []
                by_id = {}
            elif op == 0:
                vals = cmd[2] or {}
                current.append(
                    {
                        "id": None,
                        "invoice_id": vals.get("invoice_id"),
                        "base_amount": vals.get("base_amount"),
                        "apply_wht": bool(vals.get("apply_wht")),
                    }
                )
            elif op == 1:
                line_id = cmd[1]
                vals = cmd[2] or {}
                if line_id not in by_id:
                    line = self.env["account.payment.invoice.line"].browse(line_id)
                    by_id[line_id] = {
                        "id": line.id,
                        "invoice_id": line.invoice_id.id,
                        "base_amount": line.base_amount,
                        "apply_wht": line.apply_wht,
                    }
                    current.append(by_id[line_id])
                by_id[line_id].update(vals)
                if "apply_wht" in vals:
                    by_id[line_id]["apply_wht"] = bool(by_id[line_id]["apply_wht"])
            elif op in (2, 3):
                line_id = cmd[1]
                current = [d for d in current if d.get("id") != line_id]
                by_id.pop(line_id, None)
            elif op == 4:
                line_id = cmd[1]
                if line_id not in by_id:
                    line = self.env["account.payment.invoice.line"].browse(line_id)
                    d = {
                        "id": line.id,
                        "invoice_id": line.invoice_id.id,
                        "base_amount": line.base_amount,
                        "apply_wht": line.apply_wht,
                    }
                    by_id[line_id] = d
                    current.append(d)
            elif op == 6:
                ids = cmd[2] or []
                lines = self.env["account.payment.invoice.line"].browse(ids)
                current = [
                    {
                        "id": l.id,
                        "invoice_id": l.invoice_id.id,
                        "base_amount": l.base_amount,
                        "apply_wht": l.apply_wht,
                    }
                    for l in lines
                ]
                by_id = {d["id"]: d for d in current if d["id"]}
        return current

    def _compute_base_from_line_dicts(self, line_dicts, currency, company, date):
        if not any(d.get("apply_wht") for d in line_dicts):
            for d in line_dicts:
                if d.get("base_amount") or d.get("invoice_id"):
                    d["apply_wht"] = True

        base = 0.0
        for d in line_dicts:
            if not d.get("apply_wht"):
                continue
            line_base = d.get("base_amount")
            invoice_id = d.get("invoice_id")
            if (not line_base) and invoice_id:
                inv = self.env["account.move"].browse(invoice_id)
                line_base = inv.amount_untaxed
                inv_currency = inv.currency_id
                if inv_currency and currency and inv_currency != currency:
                    line_base = inv_currency._convert(line_base, currency, company, date)
            base += line_base or 0.0
        return base

    def _prepare_wht_vals_from_changes(self, vals):
        self.ensure_one()
        tax_id = vals.get("tax_id1") or self.tax_id1.id
        if not tax_id:
            return {}

        currency = self.currency_id
        if "currency_id" in vals and vals["currency_id"]:
            currency = self.env["res.currency"].browse(vals["currency_id"])

        partner = self.partner_id
        if "partner_id" in vals and vals["partner_id"]:
            partner = self.env["res.partner"].browse(vals["partner_id"])

        date = vals.get("date") or self.date or fields.Date.context_today(self)
        company = self.company_id or self.env.company
        tax = self.env["account.tax"].browse(tax_id)

        if "invoice_line_ids" in vals:
            line_dicts = self._get_invoice_line_dicts_after_commands(vals["invoice_line_ids"])
        elif "processing_invoice_ids" in vals:
            existing = self.processing_invoice_ids.ids
            ids = self._get_m2m_ids_from_commands(vals["processing_invoice_ids"], existing)
            invoices = self.env["account.move"].browse(ids)
            line_dicts = [{"invoice_id": inv.id, "base_amount": inv.amount_untaxed, "apply_wht": True} for inv in invoices]
        else:
            line_dicts = [
                {
                    "invoice_id": l.invoice_id.id,
                    "base_amount": l.base_amount,
                    "apply_wht": l.apply_wht,
                }
                for l in self.invoice_line_ids
            ]
            if (not line_dicts) and self.processing_invoice_ids:
                line_dicts = [{"invoice_id": inv.id, "base_amount": inv.amount_untaxed, "apply_wht": True} for inv in self.processing_invoice_ids]

        base = self._compute_base_from_line_dicts(line_dicts, currency, company, date)
        wht = self._compute_wht_amount_from_base(base, tax=tax, currency=currency, partner=partner)
        return {"pay_amount1": base, "wht_amount1": wht}

    @api.model_create_multi
    def create(self, vals_list):
        new_vals_list = []
        for vals in vals_list:
            v = dict(vals)
            tax_id = v.get("tax_id1")
            if tax_id and (v.get("invoice_line_ids") or v.get("processing_invoice_ids")):
                currency = self.env["res.currency"].browse(v.get("currency_id")) if v.get("currency_id") else self.env.company.currency_id
                partner = self.env["res.partner"].browse(v.get("partner_id")) if v.get("partner_id") else False
                date = v.get("date") or fields.Date.context_today(self)
                company = self.env.company
                tax = self.env["account.tax"].browse(tax_id)
                line_dicts = []
                if v.get("invoice_line_ids"):
                    for cmd in v["invoice_line_ids"]:
                        if cmd[0] == 0:
                            lv = cmd[2] or {}
                            line_dicts.append(
                                {
                                    "invoice_id": lv.get("invoice_id"),
                                    "base_amount": lv.get("base_amount"),
                                    "apply_wht": bool(lv.get("apply_wht")),
                                }
                            )
                if v.get("processing_invoice_ids") and not line_dicts:
                    ids = self._get_m2m_ids_from_commands(v["processing_invoice_ids"], [])
                    invoices = self.env["account.move"].browse(ids)
                    line_dicts = [{"invoice_id": inv.id, "base_amount": inv.amount_untaxed, "apply_wht": True} for inv in invoices]
                if line_dicts:
                    base = self._compute_base_from_line_dicts(line_dicts, currency, company, date)
                    v["pay_amount1"] = base
                    v["wht_amount1"] = self._compute_wht_amount_from_base(base, tax=tax, currency=currency, partner=partner)
            new_vals_list.append(v)
        return super().create(new_vals_list)

    def write(self, vals):
        if len(self) > 1:
            res = True
            for rec in self:
                res = res and rec.write(vals)
            return res
        new_vals = dict(vals)
        if {"invoice_line_ids", "processing_invoice_ids", "tax_id1", "currency_id", "partner_id", "date"} & set(new_vals.keys()) and (new_vals.get("tax_id1") or self.tax_id1):
            new_vals.update(self._prepare_wht_vals_from_changes(new_vals))
        return super().write(new_vals)
