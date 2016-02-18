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
#import time
from datetime import datetime, timedelta
from urlparse import urljoin
from openerp.osv import fields, osv
from openerp.tools.translate import _

class crm_lead(osv.osv):
    
    _inherit = 'crm.lead'
    
    def get_signup_url(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        route = 'from_email'
        return urljoin(base_url, "/web/%s" % (route))
    
    def send_mail(self, cr, uid, ids, context=None):
        lead_rec = self.browse(cr, uid, ids[0], context=context)
        if not lead_rec.email_from:
            raise osv.except_osv(_('Mail Error'), _('No email specified!'))
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'appointment_scheduling_management', 'meeting_request_template')[1]
        self.pool.get('mail.template').send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)
        return True
    
class calendar_event(osv.osv):
    
    _inherit = 'calendar.event'
    
    _columns = {
        'employee_id' : fields.many2one('hr.employee', 'Employee')
    }
    
    
    def do_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'open'}, context=context)
        return True
    
        
    def onchange_employee_id(self, cr, uid, ids, employee_id, start_datetime, context=None):
        if employee_id and start_datetime:
            new_start_date = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
            new_time = new_start_date + timedelta(minutes = 30)
            calendar_ids = self.search(cr, uid, [], context=context)
            for rec in self.browse(cr, uid, calendar_ids, context=context):
                if rec.employee_id.id == employee_id and start_datetime >= rec.start_datetime and start_datetime <= rec.stop_datetime:
                    raise osv.except_osv(_('Time Allocation Error'), _('Time slot which you have selected is already allocated, Please select another time!'))
            return {'value': {'stop_datetime' : new_time}}
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
