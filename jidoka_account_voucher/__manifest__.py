# -*- coding: utf-8 -*-
{
    'name': "Jidoka Account Voucher",

    'summary': """
        Account Payment Voucher""",

    'description': """
        Account Payment Voucher
    """,

    'author': "Jidoka Team",
    'website': "https://jidokasystem.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'payment',
        'sale'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        
        'views/account_voucher_views.xml',
        'views/account_voucher_multi_views.xml',
        'views/account_move_views.xml',
        'reports/template_report.xml',
        'reports/account_voucher_report.xml',
        'reports/report_views.xml',
        'wizard/account_payment_register_views.xml',
        'views/account_journal_view.xml',
        'reports/voucher_out.xml',
    ],
    'installable': True,
}
