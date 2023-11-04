{
    'name': "Modul QA/QC",

    'summary': """
        Custom Modul QA/QC""",

    'description': """
        -
    """,

    'author': "PT. Jidoka System Indonesia",
    'website': "https://jidokasystem.co.id/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','product', 'jidoka_inventory','jidoka_material','jidoka_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/group.xml',
        'data/sequence.xml',
        'views/menu.xml',
        'views/master_data_aql_views.xml',
        'views/quality_check_views.xml',
        'views/stock_picking_views.xml',
        'views/inspection_tag_card_views.xml',
        'views/lembar_pengesahan_bahan_views.xml',
        'report/inspection_tag_card_report.xml',
        'report/action_pdf_qa_qc.xml',
        'report/pdf_qa_qc.xml',
        'report/pdf_ketidaksuaian.xml',
        'wizard/inspection_tag_card_wizard_views.xml',
        'views/akar_masalah_views.xml',
        'views/tindakan_perbaikan_views.xml',
        'views/level_aql_views.xml',
        'views/product.xml',
        'views/top_coat.xml',
        'views/tes_kekuatan_cat_views.xml',
        'views/tes_rebus_views.xml',
        'views/tes_kontruksi_views.xml',
        'views/tes_packaging_views.xml',
        'views/tes_vacum_views.xml',
        'views/tes_cat_master.xml',
        'report/tes_konstruksi_report.xml',
        'report/tes_packaging_report.xml',
        'report/tes_vacum_report.xml',
        'report/report_kekuatan_cat.xml',
		'report/tes_rebus_report.xml',
        # 'wizard/report_year_inspection_tagcard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
# -*- coding: utf-8 -*-
