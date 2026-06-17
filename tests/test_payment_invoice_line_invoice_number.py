from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("at_install", "-post_install")
class TestPaymentInvoiceLineInvoiceNumber(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.partner = cls.env["res.partner"].create({"name": "Invoice Number Partner"})

        receivable_account = cls.env["account.account"].search(
            [("company_id", "=", cls.company.id), ("internal_type", "=", "receivable")],
            limit=1,
        )
        payable_account = cls.env["account.account"].search(
            [("company_id", "=", cls.company.id), ("internal_type", "=", "payable")],
            limit=1,
        )
        vals = {}
        if receivable_account:
            vals["property_account_receivable_id"] = receivable_account.id
        if payable_account:
            vals["property_account_payable_id"] = payable_account.id
        if vals:
            cls.partner.write(vals)

        cls.journal = cls.env["account.journal"].search(
            [("company_id", "=", cls.company.id), ("type", "=", "general")],
            limit=1,
        )
        if not cls.journal:
            cls.journal = cls.env["account.journal"].create(
                {
                    "name": "Test General Journal",
                    "code": "T%04d"
                    % (cls.env["account.journal"].search_count([("company_id", "=", cls.company.id)]) + 1),
                    "type": "general",
                    "company_id": cls.company.id,
                }
            )

        cls.income_account = cls.env["account.account"].search(
            [("company_id", "=", cls.company.id), ("internal_group", "=", "income")],
            limit=1,
        )
        if not cls.income_account:
            income_type = cls.env["account.account.type"].search(
                [("internal_group", "=", "income")],
                limit=1,
            )
            if not income_type:
                income_type = cls.env["account.account.type"].create(
                    {
                        "name": "Income",
                        "type": "other",
                        "internal_group": "income",
                    }
                )
            cls.income_account = cls.env["account.account"].create(
                {
                    "name": "Test Income",
                    "code": "XINVNUM%s"
                    % (cls.env["account.account"].search_count([("company_id", "=", cls.company.id)]) + 1),
                    "user_type_id": income_type.id,
                    "company_id": cls.company.id,
                }
            )

    def _create_posted_invoice(self):
        expense_account = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("internal_group", "=", "expense")],
            limit=1,
        )
        if not expense_account:
            expense_type = self.env["account.account.type"].search(
                [("internal_group", "=", "expense")],
                limit=1,
            )
            if not expense_type:
                expense_type = self.env["account.account.type"].create(
                    {
                        "name": "Expense",
                        "type": "other",
                        "internal_group": "expense",
                    }
                )
            expense_account = self.env["account.account"].create(
                {
                    "name": "Test Expense",
                    "code": "XINVNUMEXP%s"
                    % (self.env["account.account"].search_count([("company_id", "=", self.company.id)]) + 1),
                    "user_type_id": expense_type.id,
                    "company_id": self.company.id,
                }
            )

        move = self.env["account.move"].create(
            {
                "move_type": "entry",
                "journal_id": self.journal.id,
                "line_ids": [
                    (0, 0, {"name": "Debit", "debit": 100.0, "credit": 0.0, "account_id": expense_account.id}),
                    (0, 0, {"name": "Credit", "debit": 0.0, "credit": 100.0, "account_id": self.income_account.id}),
                ],
            }
        )
        move.action_post()
        return move

    def test_invoice_number_is_stored_and_computed_from_invoice_name(self):
        model = self.env["account.payment.invoice.line"]
        self.assertIn("invoice_number", model._fields)

        field = model._fields["invoice_number"]
        self.assertTrue(field.store)

        invoice_1 = self._create_posted_invoice()
        line = model.create({"invoice_id": invoice_1.id})
        self.assertEqual(line.invoice_number, invoice_1.name)

        invoice_2 = self._create_posted_invoice()
        line.write({"invoice_id": invoice_2.id})
        line.invalidate_cache(["invoice_number"])
        self.assertEqual(line.invoice_number, invoice_2.name)
