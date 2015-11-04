# -*- coding: utf-8 -*-
{
    'name': "Help_support",

    'summary': """
        module for email based support system""",

    'description': """
        New email will import as new record in this module and responsible can take action on it
    """,

    'author': "Apagen Solutions Pvt. Ltd.",
    'website': "http://www.apagen.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'GenedMedics',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        #'security/security.xml',
        'templates.xml',
        'views/help_support.xml',
        'views/seq_id.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
