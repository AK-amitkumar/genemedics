# -*- coding: utf-8 -*-
{
    'name': "CRM Genemedics",

    'summary': """
        module for CRM""",

    'description': """
        New module for CRM
    """,

    'author': "Apagen Solutions Pvt. Ltd.",
    'website': "http://www.apagen.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'GenedMedics',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm'],

    # always loaded
    'data': [
        'crm_lead_view.xml',
       
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
