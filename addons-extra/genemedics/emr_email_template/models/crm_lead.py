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

from openerp import models,fields, api, _
from datetime import datetime, timedelta
import plivo
import urllib 
import urllib2
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from dateutil.relativedelta import relativedelta

DATE_RANGE_FUNCTION = {
    'minutes': lambda interval: relativedelta(minutes=interval),
    'hour': lambda interval: relativedelta(hours=interval),
    'day': lambda interval: relativedelta(days=interval),
    'month': lambda interval: relativedelta(months=interval),
    False: lambda interval: relativedelta(0),
}

def get_datetime(date_str):
    '''Return a datetime from a date string or a datetime string'''
    # complete date time if date_str contains only a date
    now = datetime.now()
    new_server_datetime = now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
    if ' ' not in date_str:
        new_date = new_server_datetime.split(' ')
        date_str = date_str + ' ' +new_date[1]
    return datetime.strptime(date_str, DEFAULT_SERVER_DATETIME_FORMAT)


class base_action_rule(models.Model):

    _inherit = 'base.action.rule'

    @api.model
    def _check_delay(self, action, record, record_dt):
        if action.trg_date_calendar_id and action.trg_date_range_type == 'day':
            start_dt = get_datetime(record_dt)
            action_dt = self.env['resource.calendar'].schedule_days_get_date(
                action.trg_date_calendar_id.id, action.trg_date_range,
                day_date=start_dt, compute_leaves=True
            )
        else:
            delay = DATE_RANGE_FUNCTION[action.trg_date_range_type](action.trg_date_range)
            action_dt = get_datetime(record_dt) + delay
        return action_dt


class crm_lead(models.Model):

    _inherit = 'crm.lead'

    labs_due_date = fields.Date('Labs Due Date')
    lab_panel_type = fields.Char('Lab Panel Type')
    lab_result = fields.Text('Lab Result')
    refill_date = fields.Date('Refill Date')
    medication = fields.Char('Medication')
    sig = fields.Char('SIG')
    folloup_office_con_due_date = fields.Datetime('Follow Up Office Consultation Due Date')
    folloup_phone_con_due_date = fields.Datetime('Follow Up Phone Consultation Due Date')
    employee_id = fields.Many2one('hr.employee', 'Doctor')
    
    # Scheduler Method
    
    def send_new_patient_schedule_consultaion(self, cr, uid, context=None):
        ids = self.search(cr, uid, [], context=context)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.labs_due_date and rec.next_activity_id.name == 'Final new patient not schedule consultation':
                today = datetime.today()
                wdate = datetime.strptime(rec.write_date, '%Y-%m-%d %H:%M:%S')
                self.write(cr, uid, [rec.id], {'write_date' : today}, context=context)
                template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'emr_email_template', 'email_template_new_patient_not_schedule')[1]
                self.pool.get('mail.template').send_mail(cr, uid, template_id, rec.id, force_send=True, context=context)
        return True
    
    def send_non_critical_not_received_lab_result(self, cr, uid, context=None):
        ids = self.search(cr, uid, [], context=context)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.labs_due_date and rec.next_activity_id.name == 'N-C Not receive lab results':
                today = datetime.today()
                wdate = datetime.strptime(rec.write_date, '%Y-%m-%d %H:%M:%S')
                self.write(cr, uid, [rec.id], {'write_date' : today}, context=context)
                template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'emr_email_template', 'email_template_non_critical_not_received_lab_result')[1]
                self.pool.get('mail.template').send_mail(cr, uid, template_id, rec.id, force_send=True, context=context)
        return True

#    @api.multi
#    def send_labs_due(self, patient_name, address, patient_email, lab_due_date, panel_type, reason):
#        template_id = self.env['ir.model.data'].get_object_reference('emr_email_template', 'labs_due_template')[1]
#        self.env['mail.template'].browse(template_id).send_mail(self.ids[0], force_send=False, raise_exception=False)


    # Send Mail Process
    
    def get_date(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        labs_date = self.browse(cr, uid, ids[0]).labs_due_date
        ldate = datetime.strptime(labs_date, DF)
        due_date = ldate + timedelta(days=-7)
        return due_date
    
    def get_refill_date(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        refill_date = self.browse(cr, uid, ids[0]).refill_date
        rdate = datetime.strptime(refill_date, DF)
        due_date = rdate + timedelta(days=-7)
        return due_date
    
    def get_refill_date_one(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        refill_date = self.browse(cr, uid, ids[0]).refill_date
        rdate = datetime.strptime(refill_date, DF)
        due_date = rdate + timedelta(days=-1)
        return due_date
    
    def get_ivr_call(self, cr, uid, lead_id, ivr_code, context=None):
        lead_data = self.browse(cr, uid, lead_id, context=context)
        mobile = lead_data.partner_id and lead_data.partner_id.mobile
        if not mobile:
            pass
        data = {
            'phonenumber': str(mobile),
            'message': ivr_code,
            'retry': '3',
            'keypress': {"1":"YES","2":"NO"},
            'callbackurl': 'http://odoo.genemedics.com/get_input_value',
            'jobid': str(lead_id)
        }
        
        data = urllib.urlencode(data) 
        req = urllib2.Request('http://54.173.195.179/makecall/make_call.php', data) 
        response = urllib2.urlopen(req)
        the_page = response.read()
        return the_page
    
    def send_billing_information(self, cr, uid, ids, name, address, email, due_fees, refill_due, context=None):
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'emr_email_template', 'email_template_billing_information')[1]
        self.pool.get('mail.template').send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)
        return True
    
    def send_labs_due(self, cr, uid, patient_name, address, patient_email, lab_due_date, panel_type, reason, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('email', '=', patient_email)], context=context)
        if partner_id:
            partner_rec = partner_obj.browse(cr, uid, partner_id[0], context=context)
            lead_dict = {
                'partner_id' : partner_id[0],
                'name' : 'Labs Due Date Reminder',
                'street' : partner_rec.street,
                'street2' : partner_rec.street2,
                'city' : partner_rec.city,
                'state_id' : partner_rec.state_id and partner_rec.state_id.id,
                'country_id' : partner_rec.country_id and partner_rec.country_id.id,
                'zip' : partner_rec.zip,
                'labs_due_date' : lab_due_date,
                'lab_panel_type' : panel_type,
                'description' : reason,
                'email_from' : patient_email
            }
            lead_id = self.create(cr, uid, lead_dict, context=context)
        else:
            partner_dict = {
                'name' : patient_name,
                'email' : patient_email
            }
            partner_id = partner_obj.create(cr, uid, partner_dict, context=context)
            partner_rec = partner_obj.browse(cr, uid, partner_id, context=context)
            lead_dict = {
                'partner_id' : partner_id,
                'name' : 'Labs Due Date Reminder',
                'street' : partner_rec.street,
                'street2' : partner_rec.street2,
                'city' : partner_rec.city,
                'state_id' : partner_rec.state_id and partner_rec.state_id.id,
                'country_id' : partner_rec.country_id and partner_rec.country_id.id,
                'zip' : partner_rec.zip,
                'labs_due_date' : lab_due_date,
                'lab_panel_type' : panel_type,
                'description' : reason,
                'email_from' : patient_email
            }
            lead_id = self.create(cr, uid, lead_dict, context=context)
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'emr_email_template', 'email_template_labs_due')[1]
        self.pool.get('mail.template').send_mail(cr, uid, template_id, lead_id, force_send=True, context=context)
        self.get_ivr_call(cr, uid, lead_id, 'LBDUE', context)
        return True

    def send_labs_result(self, cr, uid, patient_name, address, patient_email, panel_type, lab_result, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('email', '=', patient_email)], context=context)
        if partner_id:
            partner_rec = partner_obj.browse(cr, uid, partner_id[0], context=context)
            lead_dict = {
                'partner_id' : partner_id[0],
                'name' : 'Labs Result Received',
                'street' : partner_rec.street,
                'street2' : partner_rec.street2,
                'city' : partner_rec.city,
                'state_id' : partner_rec.state_id and partner_rec.state_id.id,
                'country_id' : partner_rec.country_id and partner_rec.country_id.id,
                'zip' : partner_rec.zip,
                'lab_result' : lab_result,
                'lab_panel_type' : panel_type,
                'email_from' : patient_email
            }
            lead_id = self.create(cr, uid, lead_dict, context=context)
        else:
            partner_dict = {
                'name' : patient_name,
                'email' : patient_email
            }
            partner_id = partner_obj.create(cr, uid, partner_dict, context=context)
            partner_rec = partner_obj.browse(cr, uid, partner_id, context=context)
            lead_dict = {
                'partner_id' : partner_id,
                'name' : 'Labs Result Received',
                'street' : partner_rec.street,
                'street2' : partner_rec.street2,
                'city' : partner_rec.city,
                'state_id' : partner_rec.state_id and partner_rec.state_id.id,
                'country_id' : partner_rec.country_id and partner_rec.country_id.id,
                'zip' : partner_rec.zip,
                'lab_result' : lab_result,
                'lab_panel_type' : panel_type,
                'email_from' : patient_email
            }
            lead_id = self.create(cr, uid, lead_dict, context=context)
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'emr_email_template', 'email_template_lab_result')[1]
        self.pool.get('mail.template').send_mail(cr, uid, template_id, lead_id, force_send=True, context=context)
        self.get_ivr_call(cr, uid, lead_id, 'LBRES', context)
        return True
    
    def send_medication_refill(self, cr, uid, name, email, address, refill_date, medication, sig, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('email', '=', email)], context=context)
        if partner_id:
            partner_rec = partner_obj.browse(cr, uid, partner_id[0], context=context)
            lead_dict = {
                'partner_id' : partner_id[0],
                'name' : 'Medication Refill',
                'street' : partner_rec.street,
                'street2' : partner_rec.street2,
                'city' : partner_rec.city,
                'state_id' : partner_rec.state_id and partner_rec.state_id.id,
                'country_id' : partner_rec.country_id and partner_rec.country_id.id,
                'zip' : partner_rec.zip,
                'refill_date' : refill_date,
                'medication' : medication,
                'sig' : sig,
                'email_from' : email,
            }
            lead_id = self.create(cr, uid, lead_dict, context=context)
        else:
            partner_dict = {
                'name' : name,
                'email' : email
            }
            partner_id = partner_obj.create(cr, uid, partner_dict, context=context)
            partner_rec = partner_obj.browse(cr, uid, partner_id, context=context)
            lead_dict = {
                'partner_id' : partner_id,
                'name' : 'Medication Refill',
                'street' : partner_rec.street,
                'street2' : partner_rec.street2,
                'city' : partner_rec.city,
                'state_id' : partner_rec.state_id and partner_rec.state_id.id,
                'country_id' : partner_rec.country_id and partner_rec.country_id.id,
                'zip' : partner_rec.zip,
                'refill_date' : refill_date,
                'medication' : medication,
                'sig' : sig,
                'email_from' : email,
            }
            lead_id = self.create(cr, uid, lead_dict, context=context)
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'emr_email_template', 'email_template_medication')[1]
        self.pool.get('mail.template').send_mail(cr, uid, template_id, lead_id, force_send=True, context=context)
        self.get_ivr_call(cr, uid, lead_id, 'PRD01', context)
        return True
    
    def send_office_visit_followup(self, cr, uid, name, address, email, consulation_due, consulation_due_date, reason, dr_name, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('email', '=', email)], context=context)
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('name', '=', dr_name)], context=context)
        if employee_ids:
            employee_id = employee_ids[0]
        else:
            employee_id = self.pool.get('hr.employee').create(cr, uid, {'name' : dr_name}, context=context)
        if partner_id:
            partner_rec = partner_obj.browse(cr, uid, partner_id[0], context=context)
            lead_dict = {
                'partner_id' : partner_id[0],
                'name' : 'Follow Up Office Visit',
                'street' : partner_rec.street,
                'street2' : partner_rec.street2,
                'city' : partner_rec.city,
                'state_id' : partner_rec.state_id and partner_rec.state_id.id,
                'country_id' : partner_rec.country_id and partner_rec.country_id.id,
                'zip' : partner_rec.zip,
                'folloup_office_con_due_date' : consulation_due,
                'folloup_phone_con_due_date' : consulation_due_date,
                'description' : reason,
                'email_from' : email,
                'employee_id' : employee_id
            }
            lead_id = self.create(cr, uid, lead_dict, context=context)
        else:
            partner_dict = {
                'name' : name,
                'email' : email
            }
            partner_id = partner_obj.create(cr, uid, partner_dict, context=context)
            partner_rec = partner_obj.browse(cr, uid, partner_id, context=context)
            lead_dict = {
                'partner_id' : partner_id,
                'name' : 'Follow Up Office Visit',
                'street' : partner_rec.street,
                'street2' : partner_rec.street2,
                'city' : partner_rec.city,
                'state_id' : partner_rec.state_id and partner_rec.state_id.id,
                'country_id' : partner_rec.country_id and partner_rec.country_id.id,
                'zip' : partner_rec.zip,
                'folloup_office_con_due_date' : consulation_due,
                'folloup_phone_con_due_date' : consulation_due_date,
                'description' : reason,
                'email_from' : email,
                'employee_id' : employee_id
            }
            lead_id = self.create(cr, uid, lead_dict, context=context)
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'emr_email_template', 'email_template_appoinment_reminder_off_con')[1]
        self.pool.get('mail.template').send_mail(cr, uid, template_id, lead_id, force_send=True, context=context)
        self.get_ivr_call(cr, uid, lead_id, 'OFCOA', context)
        return True
    
    def send_due_call_followup(self, cr, uid, name, address, email, phone_call_due_date, reason, dr_name, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('email', '=', email)], context=context)
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('name', '=', dr_name)], context=context)
        if employee_ids:
            employee_id = employee_ids[0]
        else:
            employee_id = self.pool.get('hr.employee').create(cr, uid, {'name' : dr_name}, context=context)
        if partner_id:
            partner_rec = partner_obj.browse(cr, uid, partner_id[0], context=context)
            lead_dict = {
                'partner_id' : partner_id[0],
                'name' : 'Follow Up Calls Due',
                'street' : partner_rec.street,
                'street2' : partner_rec.street2,
                'city' : partner_rec.city,
                'state_id' : partner_rec.state_id and partner_rec.state_id.id,
                'country_id' : partner_rec.country_id and partner_rec.country_id.id,
                'zip' : partner_rec.zip,
                'folloup_phone_con_due_date' : phone_call_due_date,
                'description' : reason,
                'email_from' : email,
                'employee_id' : employee_id
            }
            lead_id = self.create(cr, uid, lead_dict, context=context)
        else:
            partner_dict = {
                'name' : name,
                'email' : email
            }
            partner_id = partner_obj.create(cr, uid, partner_dict, context=context)
            partner_rec = partner_obj.browse(cr, uid, partner_id, context=context)
            lead_dict = {
                'partner_id' : partner_id,
                'name' : 'Follow Up Calls Due',
                'street' : partner_rec.street,
                'street2' : partner_rec.street2,
                'city' : partner_rec.city,
                'state_id' : partner_rec.state_id and partner_rec.state_id.id,
                'country_id' : partner_rec.country_id and partner_rec.country_id.id,
                'zip' : partner_rec.zip,
                'folloup_phone_con_due_date' : phone_call_due_date,
                'description' : reason,
                'email_from' : email,
                'employee_id' : employee_id
            }
            lead_id = self.create(cr, uid, lead_dict, context=context)
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'emr_email_template', 'email_template_appoinment_reminder')[1]
        self.pool.get('mail.template').send_mail(cr, uid, template_id, lead_id, force_send=True, context=context)
        self.get_ivr_call(cr, uid, lead_id, 'PHCOA', context)
        return True
   
    def send_medical_consulation(self, cr, uid, ids, context=None):
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'emr_email_template', 'email_template_appoinment_reminder_med_con')[1]
        self.pool.get('mail.template').send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)
        return True

    def send_lab_work(self, cr, uid, ids, context=None):
        template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'emr_email_template', 'email_template_appoinment_reminder_lab_work')[1]
        self.pool.get('mail.template').send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)
        return True

    # Send SMS Process
    def send_sms(self, auth_id, auth_token, sms_content, to_number, from_number):
        auth_id = auth_id
        auth_token = auth_token
        p = plivo.RestAPI(auth_id, auth_token)
        params = {
            'src': from_number, # Sender's phone number with country code
            'dst' : to_number, # Receiver's phone Number with country code
            'text' : sms_content, # Your SMS Text Message - English
            'url' : "http://morning-ocean-4669.herokuapp.com/report/", # The URL to which with the status of the message is sent
            'method' : 'GET' # The method used to call the url
        }
        response = p.send_message(params)
        return True

    def send_billing_information_message(self, cr, uid, patient_name, address, patient_email, lab_due_date, panel_type, reason, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('email', '=', patient_email)], context=context)
        if partner_id:
            partner_rec = partner_obj.browse(cr, uid, partner_id[0], context=context)
            if partner_rec.mobile:
                auth_id = "MAMZLJZMZMMZLKMZE3NZ"
                auth_token = "NDRhZmZlZTUyOWJkYzBjNDY4N2VlYzY4YTQwNDdi"
                sms_content = u"Billing Information"
                to_number = partner_rec.mobile
                from_number = '+13306807835'
                self.send_sms(cr, uid, auth_id, auth_token, sms_content, to_number, from_number)
        return True

    def send_labs_message(self, cr, uid, ids, context=None):
#        self.send_labs_due_message('Prakash', 'Gandhinagar', 'n.mehta.serpentcs@gmail.com', '06-02-2016', 'aa', 'aa')
        return True

    def send_labs_due_message(self, cr, uid, patient_name, address, patient_email, lab_due_date, panel_type, reason, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('email', '=', patient_email)], context=context)
        if partner_id:
            partner_rec = partner_obj.browse(cr, uid, partner_id[0], context=context)
            if partner_rec.mobile:
                lab_due_date = datetime.strptime(lab_due_date, '%d-%m-%Y')
                new_lab_due_date = lab_due_date.strftime('%m-%d-%Y')
                auth_id = "MAMZLJZMZMMZLKMZE3NZ"
                auth_token = "NDRhZmZlZTUyOWJkYzBjNDY4N2VlYzY4YTQwNDdi"
                sms_content = u"Genemedics Health Institute: Our records indicate that you are due for lab work on %s.  Please call our office or log into your patient portal to obtain your lab order and schedule an appointment. www.genemedics.com/patientportalsignforms" % (new_lab_due_date)
                to_number = partner_rec.mobile
                from_number = '+13306807835'
                self.send_sms(auth_id, auth_token, sms_content, to_number, from_number)
        return True

    def send_labs_result_message(self, cr, uid, patient_name, address, patient_email, panel_type, lab_result, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('email', '=', patient_email)], context=context)
        if partner_id:
            partner_rec = partner_obj.browse(cr, uid, partner_id[0], context=context)
            if partner_rec.mobile:
                auth_id = "MAMZLJZMZMMZLKMZE3NZ"
                auth_token = "NDRhZmZlZTUyOWJkYzBjNDY4N2VlYzY4YTQwNDdi"
                sms_content = u"Lab Test"
                to_number = partner_rec.mobile
                from_number = '+13306807835'
                self.send_sms(auth_id, auth_token, sms_content, to_number, from_number)
        return True

    def send_medication_refill_message(self, cr, uid, name, email, address, refill_date, medication, sig, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('email', '=', email)], context=context)
        if partner_id:
            partner_rec = partner_obj.browse(cr, uid, partner_id[0], context=context)
            if partner_rec.mobile:
                auth_id = "MAMZLJZMZMMZLKMZE3NZ"
                auth_token = "NDRhZmZlZTUyOWJkYzBjNDY4N2VlYzY4YTQwNDdi"
                sms_content = u"Genemedics Health Institute: Our records indicate that your prescriptions will be refilled and shipped from the pharmacy on (7 days prior to run-out date).  Please contact our office or log into your patient portal to delay or cancel your order. www.genemedics.com/patientportalsignforms"
                to_number = partner_rec.mobile
                from_number = '+13306807835'
                self.send_sms(auth_id, auth_token, sms_content, to_number, from_number)
        return True

    def send_office_visit_followup_message(self, cr, uid, name, address, email, consulation_due, consulation_due_date, reason, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('email', '=', email)], context=context)
        if partner_id:
            partner_rec = partner_obj.browse(cr, uid, partner_id[0], context=context)
            if partner_rec.mobile:
                auth_id = "MAMZLJZMZMMZLKMZE3NZ"
                auth_token = "NDRhZmZlZTUyOWJkYzBjNDY4N2VlYzY4YTQwNDdi"
                sms_content = u"Hello, This is Genemedics Health Institute calling to remind you of your consultation appointment with %s for tomorrow at 10:00 A.M. at our %s location.  If for any reason you need to cancel or reschedule your appointment, please call our office at (800) 277-4041.  Thank you for choosing Genemedics Health Institute.  We look forward to seeing you tomorrow!   Have a great day! " % (name, address)
                to_number = partner_rec.mobile
                from_number = '+13306807835'
                self.send_sms(auth_id, auth_token, sms_content, to_number, from_number)
        return True

    def send_due_call_followup_message(self, cr, uid, name, address, email, phone_call_due_date, reason, context=None):
        partner_obj = self.pool.get('res.partner')
        partner_id = partner_obj.search(cr, uid, [('email', '=', email)], context=context)
        if partner_id:
            partner_rec = partner_obj.browse(cr, uid, partner_id[0], context=context)
            if partner_rec.mobile:
                auth_id = "MAMZLJZMZMMZLKMZE3NZ"
                auth_token = "NDRhZmZlZTUyOWJkYzBjNDY4N2VlYzY4YTQwNDdi"
                sms_content = u"This message is to remind you of your phone consultation appointment with Genemedics Health Institute, tomorrow at 10:00 A.M.  %s will call you at this number at 9:00 A.M.  If for any reason you need to cancel or reschedule your appointment, please call our office at (800) 277-4041." % (name)
                to_number = partner_rec.mobile
                from_number = '+13306807835'
                self.send_sms(auth_id, auth_token, sms_content, to_number, from_number)
        return True

#    def send_medical_consulation_message(self, cr, uid, ids, context=None):
#        auth_id = "MAMZLJZMZMMZLKMZE3NZ"
#        auth_token = "NDRhZmZlZTUyOWJkYzBjNDY4N2VlYzY4YTQwNDdi"
#        sms_content = u"This message is to remind you of your appointment for a medical consultation with Genemedics Health Institute, tomorrow at 10:00 A.M at our %s location. If for any reason you need to cancel or reschedule your appointment, please call our office at (800) 277-4041." % (address)
#        to_number = '+447348128412'
#        from_number = '+13306807835'
#        self.send_sms(auth_id, auth_token, sms_content, to_number, from_number)
#        return True
#
#    def send_lab_work_message(self, cr, uid, ids, context=None):
#        auth_id = "MAMZLJZMZMMZLKMZE3NZ"
#        auth_token = "NDRhZmZlZTUyOWJkYzBjNDY4N2VlYzY4YTQwNDdi"
#        sms_content = u"This message is to remind you of your phone consultation appointment with Genemedics Health Institute, tomorrow at 10:00 A.M. at our %s. Please do not eat or drink anything except water 8 hours prior to your appointment.  If for any reason you need to cancel or reschedule your appointment, please call our office at (800) 277-4041." % (address)
#        to_number = '+447348128412'
#        from_number = '+13306807835'
#        self.send_sms(auth_id, auth_token, sms_content, to_number, from_number)
#        return True


class project_issue(models.Model):
    
    _inherit = 'project.issue'
    
    lead_id = fields.Many2one('crm.lead', 'Lead')
