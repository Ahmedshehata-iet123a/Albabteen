# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Custom Bank Statment",
    "version": "16.0.1.0.0",
    "category": "Accounting",
    "license": "LGPL-3",
    "summary": "Adds Bank Transaction Model",
    "author": "Enas YAsser",
    "depends": ['base',"account",'statement_custom_account'],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/custom_bank_statment.xml",

    ],
    "demo": [],
    "installable": True,
}
