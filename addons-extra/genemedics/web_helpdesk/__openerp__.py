# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Till Today Serpent Consulting Services PVT LTD (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Web Help Desk',
    'version': '1.0.1',
    'category': 'Project',
    'summary': 'Web Help Desk',
    'description': """
    """,
    'author': 'Serpent Consulting Services Pvt. Ltd',
    'installable': True,
    'application': True,
    'depends': ['crm_helpdesk_features'],
    'data':[
        'security/helpdesk_security.xml',
        'data/data.xml',
        'views/website_view.xml',
    ],
    'auto_install': False,     
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
