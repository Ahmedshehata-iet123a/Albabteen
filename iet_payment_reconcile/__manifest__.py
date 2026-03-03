{
    'name': 'IET Payment Reconcile',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Auto FIFO reconciliation between customer payments and invoices',
    'author': 'IET - Saleh ElShrief',
    'website': "https://intelligent-experts.com/",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/reconcile_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
