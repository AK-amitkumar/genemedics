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
import pytz
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
    
class calendar_event(osv.osv):
    
    _inherit = 'calendar.event'
    
    _columns = {
        'employee_id' : fields.many2one('hr.employee', 'Employee'),
        'slot_id' : fields.many2one('slot.slot', 'Available Slot'),
        'start_date' : fields.date('Appointment Date'),
    }
    
    
    def do_confirm(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state' : 'open'}, context=context)
        return True
    
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
    
    def onchange_start_date(self, cr, uid, ids, start_date, employee_id, context=None):
        tz = context and pytz.timezone(context.get('tz', False))
        if not employee_id and not start_date:
            return {}
#        calendar_ids = self.search(cr, uid, [('employee_id', '=', employee_id)], context=context)
        slot_obj = self.pool.get('slot.slot')
#        for rec in self.browse(cr, uid, calendar_ids, context=context):
#            sdate = datetime.strptime(rec.start_datetime, '%Y-%m-%d %H:%M:%S')
##            new_sdate = server_to_local_timestamp(sdate.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', tz, True, ignore_unparsable_time=False)
#            new_date = datetime.strptime(sdate, '%Y-%m-%d %H:%M:%S')
#            today = datetime.today()
#            if new_date.day >= today.day:
        slot_ids = slot_obj.search(cr, uid, [], context=context)
        avail_slots = []
        for slot_rec in slot_obj.browse(cr, uid, slot_ids, context=context):
#            now = datetime.now()
#            new_server_datetime = now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#            new_date = new_server_datetime.split(' ')
            stdate = start_date + ' ' + slot_rec.sname
            endate = start_date + ' ' + slot_rec.ename
            start_final_date = datetime.strptime(stdate, '%Y-%m-%d %H:%M:%S')
            end_final_date = datetime.strptime(endate, '%Y-%m-%d %H:%M:%S')
            st_date = tz.localize(start_final_date, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            et_date = tz.localize(end_final_date, is_dst=None).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            events = self.search(cr, uid, [('employee_id', '=', employee_id), ('start_datetime', '>=', st_date),
                                  ('start_datetime', '<=', et_date)])
            if len(events) == 0:
                avail_slots.append(slot_rec.id)
        return {'domain': {'slot_id': [('id', 'in', avail_slots)]}}

    def onchange_employee_id(self, cr, uid, ids, employee_id, start_datetime, context=None):
#        tz = context and context.get('tz', False)
        if employee_id and start_datetime:
            new_start_date = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
            new_time = new_start_date + timedelta(minutes = 30)
#            calendar_ids = self.search(cr, uid, [], context=context)
#            calendar_ids = self.search(cr, uid, [('employee_id', '=', employee_id)], context=context)
#            slot_obj = self.pool.get('slot.slot')
#            for rec in self.browse(cr, uid, calendar_ids, context=context):
#                sdate = datetime.strptime(rec.start_datetime, '%Y-%m-%d %H:%M:%S')
#                new_sdate = server_to_local_timestamp(sdate.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', tz, True, ignore_unparsable_time=False)
#                new_date = datetime.strptime(new_sdate, '%Y-%m-%d %H:%M:%S')
#                today = datetime.today()
#                if new_date.day >= today.day:
#                    slot_ids = slot_obj.search(cr, uid, [], context=context)
#                    for slot_rec in slot_obj.browse(cr, uid, slot_ids, context=context):
#                        now = datetime.now()
#                        new_server_datetime = now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#                        new_date = new_server_datetime.split(' ')
#                        stdate = new_date[0] + ' ' + slot_rec.sname
#                        endate = new_date[0] + ' ' + slot_rec.ename
#                        if new_date >= stdate and new_date <= endate:
#                    while(h <= 21):
#                        if new_date.hour >= h and new_date.minute >= m and new_date.second >= s and new_date.hour <= h1 and new_date.minute <= m1 and new_date.second <= s1:
#                            tname = str(h) + ':' + str(m) + ':' + str(s)
#                            slot_ids = slot_obj.search(cr, uid, [('name', '=', tname)], context=context)
#                            if slot_ids:
#                                slot_obj.unlink(cr, uid, slot_ids, context=context)
#                        else:
#                            m += 30
#                            m1 += 30
#                            if m == 60:
#                                m = 0
#                                h += 1
#                            if m1 == 60:
#                                m1 = 0
#                                h1 += 1
#                else:
#                    while (h1 <= 21):
#                        tname = str(h) + ':' + str(m)
#                        slot_obj.create(cr, uid, {'name' : tname}, context=context)
#                        m += 30
#                        m1 += 30
#                        if m == 60:
#                            m = 0
#                            h += 1
#                        if m1 == 60:
#                            m1 = 0
#                            h1 += 1
#                if rec.employee_id.id == employee_id and start_datetime >= rec.start_datetime and start_datetime <= rec.stop_datetime:
            return {'value': {'stop_datetime' : new_time}}
        
class slot_slot(osv.osv):
    
    _name = 'slot.slot'
    _rec_name = 'sname'
    _columns = {
        'sname' : fields.char('Slot Start Time', size=64),
        'ename' : fields.char('Slot End Time', size=64),
        
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
