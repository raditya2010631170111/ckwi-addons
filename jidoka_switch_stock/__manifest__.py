# -*- coding: utf-8 -*-
{
    'name': "Jidoka Switch Stock",

    'summary': """
        Feature switch stock (via inventory adjustment)""",

    'description': """
        Feature switch stock (via inventory adjustment)
    """,

    'author': "Jidoka Team",
    'website': "https://jidokasystem.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'stock',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/switch_stock_views.xml',
    ],
    'installable': True,
}
