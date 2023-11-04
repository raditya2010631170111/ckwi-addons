# -*- coding: utf-8 -*-
{
    'name': "Jidoka Manufacturing",

    'summary': """
        Custome module for Manufacture process""",

    'description': """
        Custome module for Manufacture process
        author: Rp. Bimantara
    """,

    'author': "Jidoka System Indonesia",
    'website': "https://jidokasystem.co.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Manufacturing/Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['mrp','kb_mrp_production','sale'],

    # always loaded
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/sawmill_views.xml',
        'views/material_dimention_views.xml',
        'views/tag_card.xml',
        'views/mrp_production_views.xml',
        'wizard/tag_card.xml',
        'report/tag_card_report_id.xml',
        'report/action_server.xml',
    ],
}
