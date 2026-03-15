# -*- coding: utf-8 -*-
{
    'name': "odoo_account_hierarchy_custom",

    'summary': """
        code of account contain at (character of company + parent account +sequence)""",

    'description': """ code of account contain at (character of company + parent account +sequence)
    """,

    'author': "MOHAMED ABDELRHMAN",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','odoo_account_hierarchy'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ir.model.access.csv',
        'views/company.xml',
        'views/account.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
