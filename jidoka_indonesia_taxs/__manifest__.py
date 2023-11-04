# -*- coding: utf-8 -*-
{
    'name': "Jidoka Indonesia Taxs",
    'summary': """
        Jidoka Indonesia Taxs""",
    'description': """
        Jidoka Indonesia Taxs
    """,
    'author': "Jidoka Team",
    'website': "https://jidokasystem.co.id",
    'category': 'Accounting',
    'version': '0.1',
    'depends': [
        'base',
        'account',
        'base_accounting_kit'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_view.xml',
        'report/report_indonesia_tax_action.xml',
        'wizard/indonesia_tax_wizard_view.xml',
    ],
    'application': True,
}
