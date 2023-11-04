# -*- coding: utf-8 -*-
{
    'name': "Jidoka Sale",

    'summary': """
        Custome module for sales process""",

    'description': """
        Custome module for sales process
        author: Rp. Bimantara
    """,

    'author': "Jidoka System Indonesia",
    'website': "https://jidokasystem.co.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['design_process','sale_stock','sale','account','product','jidoka_marketing','stock','sales_team'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/group.xml',
        'views/menu.xml',
        'views/sale_views.xml',
        'views/res_fabric_colour.xml',
        'views/notes.xml',
        'views/sc_revisi.xml',
        'report/report_action_views.xml',
        # 'views/templates.xml',
        'report/sale_mo_report.xml',
        'report/sale_confirm.xml',
        'wizard/sale_invoice_revisi.xml',
        'wizard/revisi_timset.xml',
        
        
    ],
}
