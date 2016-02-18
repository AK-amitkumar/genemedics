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
import time
import openerp
from openerp import http
from openerp import SUPERUSER_ID
from openerp.exceptions import AccessError
from openerp.http import request
from openerp.tools.translate import _


class LeadController(http.Controller):

    @http.route('/web/from_email', type='http', auth='none')
    def receive(self, req):
        """ End-point to receive mail from an external SMTP server. """
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        calendar_obj = pool['calendar.event']
        start = time.strftime('%Y-%m-%d %H:%M:%S')
        end = time.strftime('%Y-%m-%d %H:%M:%S')
        meeting_id = calendar_obj.create(cr, SUPERUSER_ID, {'name' : 'Schedule Meeting', 'start' : start, 'stop' : end}, context=context)
        uid = request.session.authenticate(request.session.db, 'naitik.mehta@serpentcs.com', 'a')
        action_id = pool['ir.model.data'].get_object_reference(cr, SUPERUSER_ID, 'appointment_scheduling_management', 'action_schedule_meeting')[1]
        if uid is not False:
            return http.redirect_with_hash('/web#id=%s&view_type=calendar&model=calendar.event&action=%s' % (meeting_id, action_id))
        raise AccessError(_("Failed"))
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

