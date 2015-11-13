# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _ 
from datetime import datetime, timedelta  
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT 
from __builtin__ import False

class crm_lead(models.Model):
    """ CRM Lead Case """
    _inherit = "crm.lead"


    @api.one
    def _cal_age(self):
        
        delta = datetime.now() - datetime.strptime(self.create_date, DEFAULT_SERVER_DATETIME_FORMAT)
        self.age_days = int(delta.days)
        
    
    def _search_cal_age(self, operator, value):
        
        try:
            days = float(value)
        except:
            days = False
         
        assert operator in ('=', '!=', '<=','>=','<','>') and days , 'Operation not supported' 
        
        if operator == '<=': operator ='>='
        if operator == '>=': operator ='<='
        if operator == '<': operator ='>'
        if operator == '>': operator ='<'
        search_date = datetime.now() - timedelta(days=days)
        search_date = datetime.strftime(search_date,DEFAULT_SERVER_DATETIME_FORMAT)
        leads = self.env['crm.lead'].search([('create_date', operator, search_date)])
        return [('id', 'in', leads.ids)]
        
   
    customer_goal = fields.Char('Customer Goal', size = 32) 
    age_days = fields.Integer(string = "Days Old",compute="_cal_age",store=False, search='_search_cal_age')
    
    _order = 'create_date'
    
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
    def action_schedule_meeting_lead(self):
        """
        Open meeting's calendar view to schedule meeting on current opportunity.
        :return dict: dictionary value for created Meeting view
        """
        IrModelData = self.env['ir.model.data']
        res = self.env['ir.actions.act_window'].for_xml_id('crm_genemedics', 'action_calendar_event_calendar')
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