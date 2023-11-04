# -*- coding: utf-8 -*-
{
    'name': "Jidoka Sawmill",

    'summary': """
        Custom module for sawmill process""",

    'description': """
        Custom module for sawmill process
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
    'depends': ['mrp', 'stock', 'product', 'jidoka_material', 'web_domain_field'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        # 'views/stock_picking_type.xml',
        'views/sawmill.xml',
        'views/sticking.xml',
        'views/manufacturing_order.xml',
        'views/sawmill_notification.xml',
        'wizard/wiz_multi_line.xml',
        # 'views/sawmill_views.xml',
        # 'views/material_dimention_views.xml',
        # 'views/tag_card.xml',
        # 'wizard/tag_card.xml',
        # 'report/tag_card_report_id.xml',
        # 'report/action_server.xml',
    ],
}
