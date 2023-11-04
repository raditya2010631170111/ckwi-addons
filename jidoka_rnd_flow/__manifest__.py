# -*- coding: utf-8 -*-
{
    'name': "Jidoka RnD Flow",

    'summary': """
        Custome module for update rnd flow""",

    'description': """
        Custome module for update rnd flow
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
    'depends': ['design_process','jidoka_marketing','mrp','product', 'jidoka_crm_sample_request','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/design_detail_views.xml',
        'views/crm_lead_views.xml',
        'views/product_template_views.xml',
        'wizard/wizard_design_detail_revised_views.xml',
        'wizard/wizard_design_detail_assign_views.xml',
        'wizard/wizard_design_detail_confirm_views.xml',
        'report/sample_request_report_pdf.xml',
    ],
}
