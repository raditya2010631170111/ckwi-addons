# -*- coding: utf-8 -*-
{
    'name': "Jidoka Inventory",

    'summary': """
        Custome module for Inventory process""",

    'description': """
        Custome module for Inventory process
    """,

    'author': "Jidoka Team",
    'website': "https://jidokasystem.co.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','contacts','purchase','report_xlsx','delivery','product','uom','base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/res_supplier_code_views.xml',
        'views/res_size_log_views.xml',
        'views/product_template_views.xml',
        'views/stock_move_line_views.xml',
        'views/res_wood_class_views.xml',
        'views/res_master_hasil_views.xml',
        'views/res_certification_views.xml',
        # 'views/stock_production_lot_views.xml',
        'views/package_views.xml',
        'views/wood_shape_views.xml',
        'views/wood_grade_views.xml',
        # 'wizard/stock_assign_tag_card_views.xml',
        'report/bukti_penerimaan_gudang_template.xml',
        'report/surat_jalan_pabrik.xml',
        'report/report_action_views.xml', 
        'views/wood_kind.xml',
        # 'views/ket_masalah.xml',
        'data/wood_kind.xml',
        'views/species.xml',
        'views/isi_defect.xml',
    ],
}
