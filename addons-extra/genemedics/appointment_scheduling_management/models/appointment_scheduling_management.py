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
from datetime import datetime, timedelta
import pytz
from urlparse import urljoin
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

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

class calendar_event_type(osv.osv):
    
    _inherit = 'calendar.event.type'
    
    
    _columns = {
        'country_id' : fields.many2one('res.country', 'Country'),
        'state_id' : fields.many2one('res.country.state', 'State'),
        'employee_ids': fields.many2many('hr.employee', 'calendar_event_meeting_rel', string='Attendees'),
#        'employee_ids' : fields.many2many('hr.employee', 'event_meeting_rel', string='Consultant'),
        'duration' : fields.float('Duration'),
        'loc' : fields.selection([('physical_loc', 'Physical Location'), ('phone_loc', 'Phone Location')], 'Location'),
    }
    
    def onchange_country_id(self, cr, uid, ids, country_id, context=None):
        if country_id:
            state_ids = self.pool.get('res.country.state').search(cr, uid, [('country_id', '=', country_id)], context=context)
            return {'domain' : {'state_id' : [('id', 'in', state_ids)]}}
    
    
class calendar_event(osv.osv):
    
    _inherit = 'calendar.event'
    
    _columns = {
        'employee_id' : fields.many2one('hr.employee', 'Employee'),
        'employee_ids': fields.many2many('hr.employee', 'calendar_event_hr_rel', string='Attendees'),
#        'employee_ids' : fields.many2many('hr.employee', 'event_emp_rel', string='Consultant'),
        'slot_id' : fields.many2one('slot.slot', 'Available Slot'),
        'start_date' : fields.date('Appointment Date'),
        'location_id' : fields.many2one('res.country.state', 'Location'),
        'meeting_type' : fields.many2one('calendar.event.type', 'Meeting Type')
    }
    
    
    def do_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'open'}, context=context)
        return True
    
    def onchange_meeting_type(self, cr, uid, ids, meeting_type, context=None):
        if not meeting_type:
            return {}
        slot_ids = []
        meeting_rec = self.pool.get('calendar.event.type').browse(cr, uid, meeting_type, context=context)
        if meeting_rec.duration == 0.30:
            slot_ids = self.pool.get('slot.slot').search(cr, uid, [('30_duration', '=', 'True')], context=context)
        if meeting_rec.duration == 2.00:
            slot_ids = self.pool.get('slot.slot').search(cr, uid, [('2_duration', '=', 'True')], context=context)
        if meeting_rec.duration == 1.00:
            slot_ids = self.pool.get('slot.slot').search(cr, uid, [('1_duration', '=', 'True')], context=context)
        meeting_dict = {
            'location_id' : meeting_rec.state_id and meeting_rec.state_id.id,
            'employee_ids' : [(6,0,[x.id for x in meeting_rec.employee_ids])]
        }
        return {'value' : meeting_dict, 'domain' : {'slot_id' : [('id', 'in', slot_ids)]}}
    
    def onchange_slot_id(self, cr, uid, ids, slot_id, start_datetime, context=None):
        if not slot_id and not start_datetime:
            return {}
        slot_rec = self.pool.get('slot.slot').browse(cr, uid, slot_id, context=context)
        new_date = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
        new_server_datetime = new_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        new_date = new_server_datetime.split(' ')
        date = new_date[0] + ' ' + slot_rec.sname
        final_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        new_time = final_date - timedelta(hours=5,minutes = 30)
        return {'value' : {'start_datetime' : new_time}}
    
    def onchange_start_date(self, cr, uid, ids, start_date, employee_id, meeting_type, context=None):
        tz = context and pytz.timezone(context.get('tz', False))
        if not employee_id and not start_date:
            return {}
        slot_obj = self.pool.get('slot.slot')
        meeting_rec = self.pool.get('calendar.event.type').browse(cr, uid, meeting_type, context=context)
        slot_ids = slot_obj.search(cr, uid, [], context=context)
        avail_slots = []
        for slot_rec in slot_obj.browse(cr, uid, slot_ids, context=context):
            stdate = start_date + ' ' + slot_rec.sname
            endate = start_date + ' ' + slot_rec.ename
            start_final_date = datetime.strptime(stdate, '%Y-%m-%d %H:%M:%S')
            end_final_date = datetime.strptime(endate, '%Y-%m-%d %H:%M:%S')
            st_date = tz.localize(start_final_date, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            et_date = tz.localize(end_final_date, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            events = self.search(cr, uid, [('employee_id', 'in', meeting_rec.employee_ids.ids), ('start_datetime', '>=', st_date),
                                  ('start_datetime', '<=', et_date), ('meeting_type', '=', meeting_type)])
            if len(events) == 0:
                avail_slots.append(slot_rec.id)
        return {'domain': {'slot_id': [('id', 'in', avail_slots)]}}

    def onchange_employee_id(self, cr, uid, ids, employee_id, start_datetime, context=None):
        if employee_id and start_datetime:
            new_start_date = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
            new_time = new_start_date + timedelta(minutes = 30)
            return {'value': {'stop_datetime' : new_time}}
        
class slot_slot(osv.osv):
    
    _name = 'slot.slot'
    _rec_name = 'sname'
    _columns = {
        'sname' : fields.char('Slot Start Time', size=64),
        'ename' : fields.char('Slot End Time', size=64),
        '30_duration' : fields.boolean('30 Min Duration'),
        '2_duration' : fields.boolean('2 Hr Duration'),
        '1_duration' : fields.boolean('1 Hr Duration'),
    }
    
class CountryState(osv.osv):
    
    _inherit = 'res.country.state'
    
    _columns = {
        'city' : fields.char('City', size=64)
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
