{
    "name": "Auto Payment WHT",
    "version": "15.0.1.0.0",
    "depends": ["account", "dtr_payment_invoice", "dtr_taxation"],
    "author": "Nattanon / Auto-Info",
    "data": [
        "security/ir.model.access.csv",
        "views/wht_type_view.xml",
        "views/account_payment_view.xml",
    ],
    "installable": True,
    "application": False,
}
