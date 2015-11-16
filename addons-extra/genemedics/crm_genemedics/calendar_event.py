# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _     
from cgi import FieldStorage


class calendar_event(models.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'
    
    
    activity_id = fields.Many2one('crm.activity','Activity')
    opportunity_id = fields.Many2one('crm.lead', 'Opportunity')

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
        return res 
        
    @api.multi
    def action_set_lead_next_activity(self):
        
        if  self.start_date  and self.opportunity_id and \
            self.opportunity.date_action  and \
            (self.opportunity_id.date_action > self.start_date or self.opportunity_id.date_action == False):
        
            self.opportunity_id.write({
                    'next_activity_id': self.activity_id.id,
                    'date_action': self.start_date,
                    'title_action': self.name,
                    })
    
    @api.multi
    def action_set_lead_activity_done(self):
        

        if not self.activity_id:
            return
        body_html = """<div><b> Schduled Activity %s</b></div>
<div>%s</div>
<div> Completed </div>
%endif""" % (self.activity_id.name, self.activity_id.title_action)
        body_html = self.pool['mail.template'].render_template(cr, uid, body_html, 'crm.lead', lead.id, context=context)
        msg_id = lead.message_post(body_html, subtype_id=self.activity_id.subtype_id.id)
        to_clear_ids.append(lead.id)
        self.opportunity_id.write(cr, uid, [lead.id], {'last_activity_id': lead.next_activity_id.id}, context=context)

        return True
    
    
    def cancel_next_activity(self, cr, uid, ids, context=None):
        
        return self.opportunity_id.write(cr, uid, ids,  {
            'next_activity_id': False,
            'date_action': False,
            'title_action': False,
        }, context=context)
        
    
    @api.model   
    def create(self,vals): 
        
        event = super(calendar_event,self).create(vals)
        
        if self.opportunity_id and self.activity_id:
            self.action_set_lead_next_activity()
            
        return event
    
    @api.multi
    def write(self, vals):
        
        event = super(calendar_event,self).write(vals)
        
        if self.opportunity_id and self.activity_id:
            self.action_set_lead_next_activity()
            
        return
                
        