# -*- coding: utf-8 -*-

{
    'name': "Jidoka Manufacturing Report",

    'summary': """
        Custome module for Manufacture report""",

    'description': """
        Custome module for Manufacture report
    """,

    'author': "Jidoka System Indonesia",
    'website': "https://jidokasystem.co.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['jidoka_manufacturing', 'report_xlsx_helper','jidoka_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        "data/paper_format.xml",
        "data/report_data.xml",
        "reports/manufacturing_report.xml",
        "reports/rekap_gudang_report.xml",
        "reports/rekap_order.xml",
        "reports/manufacturing_summary_report.xml",
        'wizard/manufacturing_report_wizard_summary.xml',
        'wizard/manufacturing_report_wizard_view.xml',
        'wizard/rekap_gudang_report_wizard_view.xml',
        'wizard/rekap_order_wizard_view.xml',
    ],
}
