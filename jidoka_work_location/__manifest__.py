# -*- coding: utf-8 -*-
{
    'name': "Jidoka Work Location",

    'summary': """
        Jidoka Work Location""",

    'description': """
        Jidoka Work Location
    """,

    'author': "Jidoka Team",
    'website': "https://jidokasystem.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # 'depends': ['base', 'hr', 'jidoka_ist_project', 'jidoka_hr_roster'],
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/employee.xml',
        'views/work_location_menu.xml',
        'views/area_menu.xml',
    ],
    'application': True,
}
