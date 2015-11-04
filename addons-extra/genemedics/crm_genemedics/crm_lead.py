# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import logging
from operator import itemgetter
from werkzeug import url_encode

from openerp import SUPERUSER_ID
from openerp import tools, api
from openerp.addons.base.res.res_partner import format_address
#from openerp.addons.crm import crm_stage
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import email_re, email_split
#from openerp.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)

CRM_LEAD_FIELDS_TO_MERGE = ['name',
    'partner_id',
    'campaign_id',
    'company_id',
    'country_id',
    'team_id',
    'state_id',
    'stage_id',
    'medium_id',
    'source_id',
    'user_id',
    'title',
    'city',
    'contact_name',
    'description',
    'email',
    'fax',
    'mobile',
    'partner_name',
    'phone',
    'probability',
    'planned_revenue',
    'street',
    'street2',
    'zip',
    'create_date',
    'date_action_last',
    'date_action_next',
    'email_from',
    'email_cc',
    'partner_name']


class crm_lead(osv.osv):
    """ CRM Lead Case """
    _inherit = "crm.lead"

    _columns = {
        'customer_goal': fields.char('Customer Goal'),
        #'date_action': fields.datetime('Next Activity Date', select=True),
    }


    def create(self, cr, uid, vals, context=None):
        '''
        This function compose an email, Lead Creation - Sends Email to Customer
        '''
        res = super(crm_lead, self).create(cr, uid, vals, context)
        self.lead_sent_automatic(cr , uid, res, context)
        '''
        #assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
	        template_id = ir_model_data.get_object_reference(cr, uid, 'crm_genemedics', 'email_template_crm_lead')[1]
	        print "template_id", template_id
        except ValueError:
	        template_id = False
        try:
	        compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
	        compose_form_id = False 
        ctx = dict(context)
        ctx.update({
	        'default_model': 'crm.lead',
	        #'default_res_id': ids[0],
	        'default_use_template': bool(template_id),
	        'default_template_id': template_id,
	        'default_composition_mode': 'comment',
	        'mark_so_as_sent': True
        })
        '''
        
        return res

    def write(self, cr, uid, ids, vals, context=None):
        res = super(crm_lead, self).write(cr, uid, ids, vals, context=context)
        # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = fields.datetime.now()
        if vals.get('user_id') and 'date_open' not in vals:
            vals['date_open'] = fields.datetime.now()
        # stage change with new stage: update probability and date_closed
        if vals.get('stage_id') and 'probability' not in vals:
            onchange_stage_values = self.onchange_stage_id(cr, uid, ids, vals.get('stage_id'), context=context)['value']
            vals.update(onchange_stage_values)
        if vals.get('probability') >= 100 or not vals.get('active', True):
            vals['date_closed'] = fields.datetime.now()
        self.next_activity_sent_automatic(cr , uid, ids[0], context)
        return res
      
    def lead_sent_automatic(self, cr, uid, ids, context=None):
        mail_mail = self.pool.get('mail.mail')
        email_template_obj = self.pool.get('mail.template')
        ir_model_data = self.pool.get('ir.model.data')
        po = self.browse(cr, uid, ids, context=context)[0]
        context['header'] = {'object': 'Lead', 'reference': po.name}
        try:
	        template_id = ir_model_data.get_object_reference(cr, uid, 'crm_genemedics', 'email_template_crm_lead')[1]
	        print "template_id", template_id
        except ValueError:
	        template_id = False
        if template_id:
            mail_id = self.pool.get('mail.template').send_mail(cr, uid, template_id, po.id, force_send=True, context=context)
            return True            


    def send_notifications(self, cr, uid, ids, context=None):
        '''
        This function compose an email, Activity Date before 24 hour - Sends Email to Salesperson
        '''
        mail_mail = self.pool.get('mail.mail')
        email_template_obj = self.pool.get('mail.template')
        ir_model_data = self.pool.get('ir.model.data')
        po = self.browse(cr, uid, ids, context=context)[0]
        try:
	        template_id = ir_model_data.get_object_reference(cr, uid, 'crm_genemedics', 'email_template_activity_date_alert')[1]
        except ValueError:
	        template_id = False
        if template_id:
            mail_id = self.pool.get('mail.template').send_mail(cr, uid, template_id, ids[0], force_send=True, context=context)
            return True 

    def check_activity_date(self, cr, uid, ids=None, context=None):
        current_date = fields.date.context_today(self, cr, uid, context=context)
        new_date = current_date + 1
        print "current_date", new_date 
        if context is None:
            context = {}
        if not ids:
            filters = [('date_deadline', '=', new_date)]
            ids = self.search(cr, uid, filters, context=context)
        res = None
        try:
            if ids:
                for activity in self.browse(cr, uid, ids, context=context):
                    if activity.date_deadline == new_date:
                        self.send_notifications(cr, uid, [activity.id], context=context)
        except Exception:
            _logger.exception("Failed processing get activity date")
        return res
        
    def log_next_activity_done(self, cr, uid, ids, context=None, next_activity_name=False):
        #res = super(crm_lead, self).log_next_activity_done(cr, uid, ids, context)
        print"==-=-=-=-==-=log_next_activity_done"
        to_clear_ids = []
        for lead in self.browse(cr, uid, ids, context=context):
            print"::::::::::::::::----sddsdsdsdd--next_activity_id", lead.next_activity_id.id
            if not lead.next_activity_id:
                continue
            body_html = """<div><b>${object.next_activity_id.name}</b></div>
%if object.title_action:
<div>${object.title_action}</div>
%endif"""
            body_html = self.pool['mail.template'].render_template(cr, uid, body_html, 'crm.lead', lead.id, context=context)
            msg_id = lead.message_post(body_html, subtype_id=lead.next_activity_id.subtype_id.id)
            to_clear_ids.append(lead.id)
            self.write(cr, uid, [lead.id], {'last_activity_id': lead.next_activity_id.id}, context=context)
        print"==-=-=-=-==-=log_next_activity_done 1 1 1"
        #self.next_activity_sent_automatic(cr , uid, ids[0], context)
        if to_clear_ids:
            self.cancel_next_activity(cr, uid, to_clear_ids, context=context)
        return True

    def next_activity_sent_automatic(self, cr, uid, ids, context=None):
        mail_mail = self.pool.get('mail.mail')
        email_template_obj = self.pool.get('mail.template')
        ir_model_data = self.pool.get('ir.model.data')
        po = self.browse(cr, uid, ids, context=context)[0]
        print"::::::::::::::::------next_activity_id", po.date_action, po.next_activity_id.name
        #context['header'] = {'object': 'Lead', 'reference': po.name}
        if po.next_activity_id:
            try:
                if po.next_activity_id.name == 'Consultation':
	                template_id = ir_model_data.get_object_reference(cr, uid, 'crm_genemedics', 'email_template_consultation_scheduled')[1]
	                print "template_id", template_id
                if po.next_activity_id.name == 'Blood Draw':
                    template_id = ir_model_data.get_object_reference(cr, uid, 'crm_genemedics', 'email_template_blood_work_scheduled')[1]
                    print "template_id", template_id
                if po.next_activity_id.name == 'Medical Consultation':
                    template_id = ir_model_data.get_object_reference(cr, uid, 'crm_genemedics', 'email_template_medical_consultation')[1]
                    print "template_id", template_id
                if po.next_activity_id.name == 'First Attempt':
                    template_id = ir_model_data.get_object_reference(cr, uid, 'crm_genemedics', 'email_template_first_attempt')[1]
                    print "template_id", template_id
                if po.next_activity_id.name == 'After In-office consultation':
                    template_id = ir_model_data.get_object_reference(cr, uid, 'crm_genemedics', 'email_template_after_in_office')[1]
                    print "template_id", template_id
            except ValueError:
	            template_id = False
            if template_id:
                mail_id = self.pool.get('mail.template').send_mail(cr, uid, template_id, po.id, force_send=True, context=context)
                return True 
        else:
            return True
                  

