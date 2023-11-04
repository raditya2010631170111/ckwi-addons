# -*- coding: utf-8 -*-
{
    'name': "Jidoka Dynamic Accounts Report",

    'summary': """
        Custom Dynamic Accounts Report""",

    'description': """
        Custom Dynamic Accounts Report
        - multi period
        - total in bottom & remove total top
        - add custom report: cashflow, 
    """,

    'author': "Jidoka Team",
    'website': "https://jidokasystem.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'dynamic_accounts_report',
        'base_accounting_kit',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/cash_flow_config_data.xml',
        'views/assets.xml',
        'views/menu.xml',
        'views/account_financial_report.xml',
        'views/cash_flow_config_views.xml',
        'reports/financial_report.xml',
        'reports/trial_balance.xml',
    ],
    'qweb': [
        'static/src/xml/financial_reports.xml',
        'static/src/xml/trial_balance.xml',
        'static/src/xml/general_ledger.xml',
        'static/src/xml/cash_flow_custom.xml',
    ],
}
