# -*- coding: utf-8 -*-
{
    'name': "Jidoka Material Process",

    'summary': """
        Custom module for material process""",

    'description': """
        Custom module for material process
        author: Sultan Akbar Rachmawan
    """,

    'author': "Jidoka System Indonesia",
    'website': "https://jidokasystem.co.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacture',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'mrp',
        'stock',
        'jidoka_sale'
        ,'product',
        'jidoka_inventory',
        'design_process',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',

        'views/stock_location.xml',
        'views/stock_new.xml',
        'views/stock_picking_type.xml',
        'views/stock_picking.xml',
        'views/product.xml',
        'views/material.xml',
        'views/tagcard.xml',
        'views/stock_quant_package.xml',
        'views/stock_quant.xml',

        'wizard/tagcard_transfer_wiz.xml',
        'wizard/tagcard_quick_add_wiz.xml',

        'report/action_server.xml',
        'report/tag_card_report_id.xml',
        'report/tag_card_component_report.xml',
        'report/tag_card_barang_setengah_jadi_report.xml',
        'report/tag_card_barang_jadi_report.xml',
    ],
}
