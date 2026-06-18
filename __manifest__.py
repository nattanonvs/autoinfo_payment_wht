{
    "name": "AutoInfo Payment WHT",
    "version": "15.0.1.1.0",
    "license": "LGPL-3",
    "depends": ["account", "dtr_payment_invoice", "dtr_taxation"],
    "author": "Nattanon Vinyangkoon / Auto-Info, The Auto-Info Co., Ltd.",
    "summary": "Compute WHT base from selected invoices on payment",
    "description": "AutoInfo Payment WHT",
    "data": [
        "security/ir.model.access.csv",
        "views/wht_type_view.xml",
        "views/account_payment_view.xml",
    ],
    "installable": True,
    "application": False,
}
