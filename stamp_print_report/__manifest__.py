# -*- coding: utf-8 -*-
{
    'name': "stamp_print_report",

    'summary': """
        add stamp at all print pdf""",

    'description': """
       add stamp at all print pdf
    """,

    'author': "MOHAMED ABDALRAHMAN",


    'category': 'base',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','l10n_gcc_invoice'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/invoice_stamp.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
