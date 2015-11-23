# -*- coding: utf-8 -*-
{
    'name': "CRM Genemedics",

    'summary': """
        module for CRM""",

    'description': """
        Leads CRM customization for  Genemedics Health Institute
    """,

    'author': "Novapoint Group Inc, Stephen Levenhagen",
    'website': "http://novapointgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Customer Relationship Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','calendar','web_calendar'],

    # always loaded
    'data': [
        'views/sale_dashboard.xml',
        'views/web_calendar.xml',
        'security/genemedics_security.xml',    
        'crm_lead_view.xml',
        'calendar_event_view.xml',
        'crm_leads_menu.xml',
      
    ],
     'js': ['static/js/web_calendar.js',
            ],
     'qweb':['static/src/xml/sales_manager_dashboard.xml'],
     }
