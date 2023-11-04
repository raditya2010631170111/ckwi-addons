# -*- coding: utf-8 -*-
{
    'name': "Jidoka Export",

    'summary': """
        Module export for CKWI""",

    'description': """
        Module export for CKWI
    """,

    'author': "Jidoka Team",
    'website': "https://jidokasystem.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product',
        'jidoka_inventory',
        'stock',
        'design_process',
        'account',
        'jidoka_sale',
        'sale',
        'sale_stock', 
        'uom',
        'report_xlsx' 
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'report/shipping_ins.xml',
        'report/packing_list.xml',
        'report/invoice.xml',
        'views/packing_list.xml',
        'views/shipping_ins.xml',
        'views/invoice.xml',
        'views/stock_move_views.xml',
        'views/stock_move_line_views.xml',
        'views/sale.xml',
        'views/stock_picking.xml',
    ],
}
