# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
import openerp
from openerp import http
from openerp import SUPERUSER_ID
from openerp.exceptions import AccessError
from openerp.http import request
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class website_input_value(http.Controller):
    
    @http.route('/get_input_value', type='http', method='post', website=True)
    def input_value(self, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        lead_obj = pool['crm.lead']
        if kw.get('keypress') == 'YES':
            crm_act_ids = pool['crm.activity'].search(cr, uid, [('name', '=', 'Schedule Medical Consultation')], context=context)
            if crm_act_ids:
                lead_obj.write(cr, uid, [int(kw.get('jobid'))], {'next_activity_id' : crm_act_ids[0]}, context=context)
        if kw.get('keypress') == 'NO' or kw.get('keypress') == 'RESCHEDULE':
            lead_ids = lead_obj.search(cr, uid, [('id', '=', int(kw.get('jobid')))], context=context)
            prj_ids = pool['project.project'].search(cr, uid, [('name', '=', 'Helpdesk')], context=context)
            for lead in lead_obj.browse(cr, uid, lead_ids, context=context):
                issue_dict = {
                    'name' : lead.name,
                    'user_id' : lead.user_id and lead.user_id.id,
                    'project_id' : prj_ids and prj_ids[0],
                    'partner_id' : lead.partner_id and lead.partner_id.id,
                    'email_from' : lead.email_from,
                    'lead_id' : int(kw.get('jobid')),
                }
                pool['project.issue'].create(cr, uid, issue_dict, context=context)
        return True

