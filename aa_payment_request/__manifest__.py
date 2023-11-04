{
    'name': 'Payment Request',
    'summary': 'Accounting - Payment Request',
    'description': """
        Submenu baru pada menu Accounting yang memiliki fitur untuk meminta atau mengembalikan uang kepada finance
    """,
    'author': "PT. Ismata Nusantara Abadi",

    'website': "https://ismata.co.id/",

    'category': 'Accounting/Accounting',

    
    'depends': [
        'base',
        'account',
        'mail',
        'hr',
        'jidoka_work_location',
        'jidoka_account_voucher',
    ],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_config_views.xml',
        'report/report_bank_cash_views.xml',
        'views/view.xml',
        'views/company.xml',
        'report/report_action.xml',
        'report/print_out.xml',
        'views/jidoka_worklocation_view.xml',
        'views/account_journal_view.xml',
        'data/template_email_petty_cash.xml',
        'wizard/reject_reason_petty_cash_wizard.xml',
        'views/res_users_view.xml',
    ],
    # 'images': [],
    # 'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
