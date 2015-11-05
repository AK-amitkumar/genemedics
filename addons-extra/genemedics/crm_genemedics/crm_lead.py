# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, _     

class crm_lead(models.Model):
    """ CRM Lead Case """
    _inherit = "crm.lead"

    
    customer_goal = fields.Char('Customer Goal', size = 32) 

