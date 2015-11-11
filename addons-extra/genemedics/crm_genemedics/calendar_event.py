# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _     


class calendar_event(models.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'
    
    activity_id = fields.Many2one('crm.activity','Activity')
    
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
        