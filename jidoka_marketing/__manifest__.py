# -*- coding: utf-8 -*-
{
    'name': "Jidoka Marketing",

    'summary': """
        Team Marketing

        """,
    'description': """
        - CRM
        - Sale
    """,
    'author': "asop-source",
    'category': 'crm',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','sale','mrp','jidoka_inventory','product','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/contract_reviews.xml',
        'wizard/approval_history.xml',
        'data/ir_config_parameter.xml',
        'data/mail_template.xml',
        'data/mail_template_reject.xml',
        'views/crm.xml',
        'views/sale.xml',
        'views/meterial.xml',
        'views/finish.xml',
        'views/menu.xml',
        'data/ir_sequence.xml',
        'report/format_paper.xml',
        'report/menu.xml',
        'report/spec_design.xml',
        'report/sale_confirm.xml',
        'report/contract_reviews.xml',
        'security/security.xml',  # HIDE BELUM DIPAKAI
    ],

}
