# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _     
from cgi import FieldStorage
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT 
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime, timedelta  


class calendar_event(models.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'
    
    
    activity_id = fields.Many2one('crm.activity','Activity')
    opportunity_id = fields.Many2one('crm.lead', 'Opportunity')
    activity_done = fields.Boolean('Activity Complete')
    activity_date = fields.Date('Activity Planned')

    @api.model
    def default_get(self, fields):
        context = self._context or {}
        res = super(calendar_event, self).default_get(fields)
         
        res['opportunity_id'] = context.get('default_opportunity_id',False)
        res['partner_id'] = context.get('default_partner_id',False) 
        res['partner_ids'] = context.get('default_partner_ids',False) 
        res['team_id'] = context.get('default_team_id',False)
        res['name'] = context.get('default_name',False)
        res['activity_id'] =  context.get('default_activity_id',False)
        res['activity_date'] = context.get('default_activity_date',False)
        res['user_id'] = context.get('default_user_id', False)
        res['all_day'] = context.get('default_all_day', False)
        return res 
        
    @api.multi
    def action_set_lead_next_activity(self):
        
        lead = self.opportunity_id
        
        cal_event_start = self.start and datetime.strptime(self.start,DEFAULT_SERVER_DATETIME_FORMAT ) or False
        lead_action_date = lead.date_action and datetime.strptime(lead.date_action,DEFAULT_SERVER_DATE_FORMAT) or False
        if   self.opportunity_id and cal_event_start  and\
            not lead_action_date or (lead_action_date > cal_event_start ):
        
            if self.search([('opportunity_id','=',lead.id), ('activity_done','=',False), ('start','<',self.start)]):
                return
            else:
                lead.write({
                    'next_activity_id': self.activity_id.id,
                    'date_action': datetime.strftime(cal_event_start,DEFAULT_SERVER_DATE_FORMAT),
                    'title_action': self.name,
                    })
                return
    
    @api.multi
    def action_set_lead_activity_done(self):
        
        lead = self.opportunity_id
        if not self.activity_id:
            return
        body_html = """<div><b> Schduled Activity %s</b></div>
<div>%s</div>
<div> Completed </div>
""" % (self.name, self.description)
        body_html = self.env['mail.template'].render_template( body_html, 'crm.lead', lead.id)
        msg_id = lead.message_post(body_html, subtype_id=self.activity_id.subtype_id.id)
       
        self.opportunity_id.write({'last_activity_id': lead.next_activity_id.id, 'date_action_last': fields.datetime.now})
        self.activity_done = True
        self.cancel_next_activity()

        return true
    
        
    @api.multi    
    def cancel_next_activity(self):
        
        self.opportunity_id.write( {
            'next_activity_id': False,
            'date_action': False,
            'title_action': False,
        })
        

    
    @api.multi
    def write(self, vals):
        
        event = super(calendar_event,self).write(vals)
        
        if self.opportunity_id and self.activity_id:
            self.action_set_lead_next_activity()
            
        return
                
        