# -*- coding: utf-8 -*-
{
    'name': "Jidoka Purchase",

    'summary': """
        Custome module for purchase process""",

    'description': """
        Custome module for purchase process
        author: Rp. Bimantara
    """,

    'author': "Jidoka System Indonesia",
    'website': "https://jidokasystem.co.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','purchase_requisition','jidoka_inventory','report_xlsx','account', 'qa_qc', 'stock','purchase_stock','product','purchase_order_type'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/purchase_requisition_views.xml',
        'views/purchase_order_views.xml',
        'views/res_users_views.xml',
        'views/res_location_views.xml',
        'views/grading_summary_views.xml',
        'views/rekapitulasi_grading_views.xml',
        'views/stock_picking_views.xml',
        # 'views/stock_backorder_confirmation.xml',
        # 'views/wood_grade_views.xml', dipindahkan ke jidoka inventory
        'views/stock_picking_return.xml',
        'report/report_action_views.xml',
        'report/po_reguler_report.xml',
        'report/purchase_order_template.xml',
        'report/report_invoice_local.xml',
        'report/report_grading_summary_pdf.xml',
        # 'views/account_views.xml',
    ],
}
