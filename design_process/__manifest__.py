# -*- coding: utf-8 -*-
{
    'name': "Design Process",
    'summary': """
        Process R & D
    """,
    'description': """
        Process R & D
    """,
    'author': "asop-source",
    'website': "http://www.nusagarda.com",

    'category': 'sale',
    'version': '0.1',
    'depends': ['base','crm','product', 'stock', 'resource','sale','jidoka_marketing','sale_crm','mrp','report_xlsx','hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/group_user.xml',
        'data/stage_view.xml',
        'data/ir_sequence.xml',
        'data/mail_template_crm_manager.xml',
        'data/ir_config_parameter.xml',
        'report/bom_structure.xml',
        'wizard/approval_history.xml',
        'wizard/manufacture_order.xml',
        'wizard/reason_crm.xml',
        'views/design_process.xml',
        'views/costing_views.xml',
        'views/crm.xml',
        'views/manufacture_order.xml',
        'views/stage.xml',
        'views/product.xml',
        'views/sale.xml',
        'views/proportion.xml',
        'views/team_rnd.xml',
        'views/sample_request.xml',
        'views/menu.xml',
        'static/src/xml/rnd_bom_report.xml',
        
        'report/format_paper.xml',
        'report/report.xml',
        'report/contract_reviews.xml',
        'report/sample_request_report_pdf.xml'
    ],
}
