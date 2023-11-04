# -*- coding: utf-8 -*-
{
    'name': "Jidoka_AWB",

    'summary': """
        Custome module for Inventory AWB""",

    'description': """
        Custome module for Inventory AWB
        author: Ammar Al Faruqi
    """,

    'author': "Ammar Al Faruqi",
    'website': "-",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','product', 'stock', 'resource','sale','jidoka_marketing','sale_crm','mrp','report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/awb_view.xml',
        'views/stock_picking_batch_view.xml',
        'views/account_move_view.xml',
        'report/surat_jalan_pabrik.xml',
        'data/ir.sequence.xml',

        # 'report/report_awb.xml'
    ],
}
