# -*- coding: utf-8 -*-

{
    "name": "Sale MO Report",
    'version': '14.0.0.0',
    "category": 'Sale',
    "summary": ' Print with MO reports in Sale',
    'sequence': 1,
    "description": """"  """,
    "author": "taufikid",
    "website": "http://www.taufikid.com",
    'license': 'LGPL-3',
    'depends': ['base','sale','mrp','crm'],
    'data': [
        'report/sale_mo_report.xml',
        'report/sale_format_report.xml',
        'views/sale.xml',
    ],
    'images': ['static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}
