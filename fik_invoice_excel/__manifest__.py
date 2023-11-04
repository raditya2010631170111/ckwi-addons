{
    "name": "Invoice Report Excel",
    "author": "taufikid",
    "version": "1.0.0",
    "category": "",
    "website": 'https://taufikid.com',
    "summary": "",
    "description": """
                    Invoice Report Excel
            
        """,
    "depends": [
        "base","account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/invoice_report_views.xml",
        "views/invoice_views.xml"
    ],
    "license": 'LGPL-3', 
    "installable": True 
}
