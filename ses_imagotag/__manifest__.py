# -*- coding: utf-8 -*-
{
    'name': "Etiquettes Electroniques",

    'summary': """
        Manage your labels. Link products to labels. Change templates.""",

    'description': """
        Manage your electronics labels. Link your products to labels that will display informations about the products
    """,

    'images': ['images/main_screenshot.png'],
    'author': "Bastien BASCOU, SES-imagotag",
    'installable': True,
    'application': True,
    'website': "www.ses-imagotag.com",


    'category': 'Marketing, Inventory, Point of Sale, Warehouse, eCommerce, Productivity',
    'version': '0.1',

    'depends': ['point_of_sale'],

    'data': [
        'security/ir.model.access.csv',
        'views/label.xml',
        'views/templates.xml',
        'views/matchings.xml',
        'views/product.xml',
    ],
}