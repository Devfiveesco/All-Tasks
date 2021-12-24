# -*- coding: utf-8 -*-

{
    'name': "ESCO hr",

    'summary': """ESCO HR""",

    'description': """ """,
    'version': '15.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'company': 'Esco',
    'website': "https://www.escoiq.com",
    'depends': ['base_setup', 'hr_holidays'],
    'data': [
        'views/leave_request.xml',
        'security/ir.model.access.csv',
        'security/security.xml'
    ],
    'images': ['static/description/banner.png'],
    'license': "AGPL-3",
    'installable': True,
    'auto_install': False,
    'application': True,
}
