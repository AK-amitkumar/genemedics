# -*- coding: utf-8 -*-
{
    'name': "CRM Phone Logs",

    'summary': """
        module for CRM""",

    'description': """
        Leads CRM custimization Logging Phone Calls
    """,

    'author': "Novapoint Group Inc, Stephen Levenhagen",
    'website': "http://novapointgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Customer Relationship Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm'],

    # always loaded
    'data': [
#        'views/crm_phonecall_data.xml', 
        'views/crm_report_view.xml',
        'security/phone_log_security.xml',
        'wizard/crm_phonecall_to_meeting_view.xml',
        'wizard/crm_phonecall_to_phonecall_view.xml',
        'views/crm_phonecall_view.xml',
        'views/crm_phonecall_menu.xml',
       
        ],
    # only loaded in demonstration mode
    'demo': [
             ],
}
