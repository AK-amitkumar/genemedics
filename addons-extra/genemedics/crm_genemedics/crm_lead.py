# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _     
from __builtin__ import False

class crm_lead(models.Model):
    """ CRM Lead Case """
    _inherit = "crm.lead"

    
    customer_goal = fields.Char('Customer Goal', size = 32) 
    
    @api.multi
    def action_schedule_meeting(self):
        
        res = super(crm_lead,self).action_schedule_meeting()
        lead = self
        name = (lead.next_activity_id and lead.next_activity_id.name) or False
        if name: 
            name = ('[%s] - %s ' %(name, lead.name))
        else: 
            name = lead.name
        res['context']['default_name'] =  name
        res['context']['default_activity_id'] = lead.next_activity_id and lead.next_activity_id.id or False
        return res
    
    @api.multi
    def action_schedule_meeting_form(self):
        """
        Open meeting's calendar view to schedule meeting on current opportunity.
        :return dict: dictionary value for created Meeting view
        """
        IrModelData = self.env['ir.model.data']
        res = self.env['ir.actions.act_window'].for_xml_id('crm_genemedics', 'action_calendar_event_form')
        lead = self
        
        partner_ids = [self.user_id.partner_id.id]
        if lead.partner_id:
            partner_ids.append(lead.partner_id.id)
            
        name = (lead.next_activity_id and lead.next_activity_id.name) or False
                
        if name: 
            name = ('[%s] - %s ' %(name, lead.name))
        else: 
            name = lead.name
        
        context = self._context.copy()
        
        context['default_opportunity_id'] = (lead.type == 'opportunity' and lead.id or False)
        context['default_partner_id'] = lead.partner_id and lead.partner_id.id or False
        context['default_partner_ids'] = partner_ids
        context['default_team_id'] = lead.team_id and lead.team_id.id or False
        context['default_name'] =  name
        context['default_activity_id'] = lead.next_activity_id and lead.next_activity_id.id or False
       
      
        res['context'] = context
                        
                                   
                                   
        return res