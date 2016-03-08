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
from datetime import datetime, timedelta
import pytz
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class website_appointment_scheduling(http.Controller):
    
#    @http.route('/appointment', type='json', auth="public", website=True)
#    def fetch_employee(self, **kw):
#        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
#        employee_obj = pool['hr.employee']
#        state_obj = pool['res.country.state']
#        partner_title = pool['res.partner.title']
#        emp_ids = employee_obj.search(cr, uid, [], context=context)
#        state_ids = state_obj.search(cr, uid, [('country_id', 'in', country_ids)], context=context)
#        title_ids = partner_title.search(cr, uid, [], context=context)
#        data = {
#            'name': employee_obj.browse(cr, uid, emp_ids, context=context),
#            'partner_title': partner_title.browse(cr, uid, title_ids, context=context),
#            'state': state_obj.browse(cr, SUPERUSER_ID, state_ids, context=context),
#        }
#        return data
    
    @http.route('/search_slot', type='json', auth="public", method='post', website=True)
    def search_slot(self, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        slot = []
        slot_obj = pool['slot.slot']
        slot_ids = slot_obj.search(cr, uid, [], context=context)
        meeting_rec = pool['calendar.event.type'].browse(cr, SUPERUSER_ID, int(kw.get('meeting_type')), context=context)
        for slot_rec in slot_obj.browse(cr, uid, slot_ids, context=context):
            employee = False
            st_date = datetime.strptime(datetime.strftime(datetime.strptime(kw.get('adate'), '%d/%m/%Y'), '%Y-%m-%d') + ' ' + slot_rec.sname, '%Y-%m-%d %H:%M:%S')
            start_date = datetime.strftime((st_date + timedelta(seconds=1)), DEFAULT_SERVER_DATETIME_FORMAT)
            end_date = datetime.strftime(st_date + timedelta(hours=meeting_rec.duration, seconds=-1), DEFAULT_SERVER_DATETIME_FORMAT)
            for consultant in meeting_rec.consultant_ids:
                cr.execute("select id from calendar_event where "\
#                        "location_id="+ str(int(kw.get('location_id'))) +" and "\
                        "employee_id="+ str(consultant.employee_id.id) +" and "\
                        "(((start_datetime between '"+start_date+"' and '"+end_date+"') or (stop_datetime between '"+start_date+"' and '"+end_date+"')) or "\
                        "(start_datetime = '"+start_date+"' and stop_datetime = '"+end_date+"') or "\
                        "('"+start_date+"' between start_datetime and stop_datetime))")
                if not cr.fetchall():
                    employee = consultant.employee_id.id
                    break
            res = {'avail': True, 'name': slot_rec.sname, 'employee': employee}
            if employee:
                res.update({'avail': False})
            slot.append(res)
        return request.website._render('appointment_scheduling_management.display_time_slot', {'slot': slot})

    @http.route('/meeting_type_onchange', type='json', method='post', website=True)
    def meeting_type_onchange(self, **kw):
        emp = []
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        vals = pool['calendar.event'].onchange_meeting_type(cr, SUPERUSER_ID, [], int(kw.get('meeting_type')), context=context)
        for employee in pool['hr.employee'].browse(cr, SUPERUSER_ID, vals.get('value').get('employee_ids')[0][2], context=context):
            emp.append([employee.id, str(employee.name)])
        return {
            'employee_ids': emp,
            'slot_id': vals.get('domain').get('slot_id')[0][2],
            'location_id': int(vals.get('value').get('location_id')),
            'list_employee_ids': vals.get('value').get('employee_ids')[0][2]
        }

    @http.route('/meeting_type', type='json', auth="public", method='post', website=True)
    def meeting_type(self, **kwargs):
        data = []
        domain = []
        state_id = int(kwargs.get('state_id'))
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        meeting_obj = pool['calendar.event.type']
        loc_ids = pool['res.country.state'].search(cr, SUPERUSER_ID, ['|', ('code', '=', 'MI'), '|', ('code', '=', 'AZ'), ('code', '=', 'FL')], context=context)
        if state_id not in loc_ids:
            domain.append(('state_id', '=', False))
        else:
            domain.append(('state_id', '=', state_id))
        type_ids = meeting_obj.search(cr, SUPERUSER_ID, domain, context=context)
        for rec in meeting_obj.browse(cr, SUPERUSER_ID, type_ids, context=context):
            data.append([rec.id, rec.name, rec.loc])
        return data

    @http.route('/employees', type='json', auth="public", method='post', website=True)
    def employees(self, **kwargs):
        data = []
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        event_type_obj = request.registry['calendar.event.type']
        for rec in event_type_obj.browse(cr, SUPERUSER_ID, int(kwargs.get('meeting_type')), context=context).employee_ids:
            data.append([rec.id, rec.name])
        return data

    @http.route('/create_appointment', type='json', auth="public", method='post', website=True)
    def create_appointment(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        event_obj = request.registry['calendar.event']
        event_type_obj = request.registry['calendar.event.type']
        start_datetime = datetime.strptime(kwargs.get('date') + ' ' + kwargs.get('time_slot'), '%d/%m/%Y %H:%M:%S').strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        duration = event_type_obj.browse(cr, SUPERUSER_ID, int(kwargs.get('meeting_type')), context=context).duration
        vals = {
            'name': 'Appointment Event',
            'employee_id': int(kwargs.get('employee_id')),
            'location_id': int(kwargs.get('location_id')),
            'meeting_type': int(kwargs.get('meeting_type')),
            'start_datetime': start_datetime,
            'state': 'open',
            'duration': duration,
        }
        onchange_vals = event_obj.onchange_duration(cr, SUPERUSER_ID, [], start_datetime, duration, context=context)
        vals.update(onchange_vals.get('value'))
        event_id = event_obj.create(cr, SUPERUSER_ID, vals, context=context)
        
        template_id = pool['ir.model.data'].get_object_reference(cr, uid, 'appointment_scheduling_management', 'consultant_notification_template')[1]
        msg_id = pool['mail.template'].send_mail(cr, uid, template_id, event_id, force_send=False, context=context)
        if msg_id:
            pool['mail.mail'].send(cr, uid, [msg_id], context=context)
        return True

    @http.route('/check_user_group', type='json', auth="public", method='post', website=True)
    def check_user_group(self, **kwargs):
        return request.registry['res.users'].has_group(request.cr, request.uid, 'appointment_scheduling_management.lead_user')


    @http.route('/appointment', type='http', auth="public", website=True, csrf=False)
    def appointment(self, **kwargs):
#        if not kwargs:
#            return request.website.render("appointment_scheduling_management.register")
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        event_obj = request.registry['calendar.event']
        slot_obj = request.registry['slot.slot']
        location_obj = pool['res.country.state']
        res_country_obj = pool['res.country']
        employee_obj = pool['hr.employee']
        meeting_obj = pool['calendar.event.type']
        res_country_ids = res_country_obj.search(cr, SUPERUSER_ID, [('code', '=', 'US')], limit=1,context=context)
        emp_ids = employee_obj.search(cr, SUPERUSER_ID, [], context=context)
        loc_ids = location_obj.search(cr, SUPERUSER_ID, [('country_id', '=', res_country_ids[0])], context=context)
        type_ids = meeting_obj.search(cr, SUPERUSER_ID, [], context=context)
        data = {
            'name': employee_obj.browse(cr, SUPERUSER_ID, emp_ids, context=context),
            'loc_name' : location_obj.browse(cr, SUPERUSER_ID, loc_ids, context=context),
#            'meeting_name' : meeting_obj.browse(cr, SUPERUSER_ID, type_ids, context=context),
        }
#        slot_ids = slot_obj.search(cr, uid, [('sname', '=', kwargs.get('slot'))], context=context)
#        slot_rec = slot_obj.browse(cr, uid, slot_ids[0], context=context)
#        new_sdate = datetime.strptime(kwargs.get('adate'), '%d/%m/%Y')
#        start_date = new_sdate.strftime('%Y-%m-%d')
#        stdate = start_date + ' ' + slot_rec.sname
#        endate = start_date + ' ' + slot_rec.ename
#        start_final_date = datetime.strptime(stdate, '%Y-%m-%d %H:%M:%S')
##        end_final_date = datetime.strptime(endate, '%Y-%m-%d %H:%M:%S')
#        new_start_date = datetime.strptime(endate, '%Y-%m-%d %H:%M:%S')
#        new_time = new_start_date + timedelta(minutes = 30)
#        even_dict = {
#            'name' : 'Medical/Free Consultation',
#            'employee_id' : int(kwargs.get('employee_id')),
#            'slot_id' : slot_ids and slot_ids[0],
#            'start_date' : start_date,
#            'start_datetime' : start_final_date,
#            'stop_datetime' : start_date
#        }
#        event_id = event_obj.create(cr, uid, even_dict, context=context)
#        slot_rec = slot_obj.browse(cr, uid, slot_id, context=context)
#        new_date = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
#        new_server_datetime = new_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
#        new_date = new_server_datetime.split(' ')
#        date = new_date[0] + ' ' + slot_rec.sname
#        final_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
#        new_time = final_date - timedelta(hours=5,minutes = 30)

        return request.website.render("appointment_scheduling_management.appointment_scheduling", data)



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
            return http.redirect_with_hash('/appointment')
        raise AccessError(_("Failed"))
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

