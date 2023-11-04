# -*- coding: utf-8 -*-
{
    'name': "Jidoka CRM Sample Request",

    'summary': """
        Sample Request CKWI""",

    'description': """
        Sample Request CKWI
    """,

    'author': "Jidoka Team",
    'website': "https://jidokasystem.co.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'base', 'crm', 'mrp', 'sale', 'jidoka_marketing', 'design_process'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/group.xml',
        'wizard/approval.xml',
        'data/ir_sequence.xml',
        'data/ir_config_parameter.xml',
        'data/mail_template.xml',
        'views/crm_menu_views.xml',
        'views/sample_request_views.xml',
        'views/mrp_production_views.xml',
        'views/sale.xml',
        'views/design_process_views.xml',
        'views/inherit_product_views.xml',
        'report/sample_request_report_pdf.xml',
    ],
}
