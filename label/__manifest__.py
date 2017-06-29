# -*- coding: utf-8 -*-
{
    'name': "Label Manager",

    'summary': """
        Manage your labels. Link products to labels. Change templates.""",

    'description': """
        Manage your labels. Link your products to labels that will display informations about the products
    """,

    'author': "Bastien BASCOU, SES-imagotag",
    'installable': True,
    'application': True,
    'website': "www.ses-imagotag.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Inventory, Point of Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/label.xml',
        'views/templates.xml',
        'views/matchings.xml',
        'views/product.xml',
    ],
}