# -*- encoding: utf-8 -*-

{
    'name': 'ESCO Manual Income Registration',

    'depends': ['account'],

    'depends': ['account', 'uom', 'product' , 'sale'],
    'author': 'Engineering Solutions ESCO',
    'website': 'www.escoiq.com',
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/income_reg_view.xml',
        'views/sales_team_view.xml'
    ],
   
    'application': True,
    'installable': True,
}
