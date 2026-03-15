# -- coding: utf-8 --
##############################################################################
#
#    Odoo,
#    Copyright (C) 2023 dev: Ahmed Nazmy.
#    Mob. +966 582122642
#    Email. a.nazmy@joudtech
#
##############################################################################
# -*- coding: utf-8 -*-
{
    'name': " Custom Invoice Module",

    'summary': """
      Module for add some requirements to the invoices and customize the invoice report
      
      """,

    'description': """
       Module for add some requirements to the invoice 
    """,

    'author': "Joudtech",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'l10n_sa', 'l10n_gcc_invoice','partner_field_translate'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/paper_format.xml',
        'data/res_company_data.xml',
        'views/res_partner_inherit.xml',
        'views/account_move_inherit.xml',
        'reports/custom_header_footer.xml',
        'reports/report_invoice_inherit.xml',
    ],
}
