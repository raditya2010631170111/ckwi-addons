# -*- coding: utf-8 -*-
{
    'name': "Jidoka Academy",

    'summary': """
        Magang PT. Jidoka System Indonesia""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Jidoka Team",
    'website': "https://www.jidokasystem.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    'data': [   # always loaded
        'views/course.xml',
        'security/ir.model.access.csv',
        'data/course_data.xml',
        'reports/session_report.xml',
        'wizards/wizard_attendees.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
