# -*- coding: utf-8 -*-
{
    'name': "running_balance_accounting",

    'summary': """
        Show running Balance At Dashboard Accounting""",

    'description': """
       Show running Balance At Dashboard Accounting
    """,

    'author': "MOHAMED ABDALRHMAN",
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',

    ],

}
