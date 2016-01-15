# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, tools, _ 
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT 
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


from __builtin__ import False

class project_issue(models.Model):
    """ CRM Lead Case """
    _inherit = "project.issue"

    @api.one
    def _cal_age_issue(self):
        
        delta = datetime.now() - datetime.strptime(self.create_date, DEFAULT_SERVER_DATETIME_FORMAT)
        hours = delta.days * 24.0 + delta.seconds / 3600.0
        self.age_issue = hours
               
        
    def _search_age_issue(self, operator, value=False):
        
        
         
        assert operator in ('=', '!=', '<=','>=','<','>') and days , 'Operation not supported' 
        
        if operator == '<=': operator ='>='
        if operator == '>=': operator ='<='
        if operator == '<': operator ='>'
        if operator == '>': operator ='<'
        search_date = datetime.now() - timedelta(hours=value)
        search_date = datetime.strftime(search_date,DEFAULT_SERVER_DATETIME_FORMAT)
        issues = self.env['project.issue'].search([('create_date', operator, search_date)])
        return [('id', 'in', leads.ids)]
        
    @api.one
    def _cal_update_age_issue(self):
        
        delta = datetime.now() - datetime.strptime(self.date_action_last, DEFAULT_SERVER_DATETIME_FORMAT)
        hours = delta.days * 24.0 + delta.seconds / 3600.0
        self.age_since_update = hours
               
        
    def _search_update_age_issue(self, operator, value=False):
        
        
         
        assert operator in ('=', '!=', '<=','>=','<','>') and days , 'Operation not supported' 
        
        if operator == '<=': operator ='>='
        if operator == '>=': operator ='<='
        if operator == '<': operator ='>'
        if operator == '>': operator ='<'
        search_date = datetime.now() - timedelta(hours=value)
        search_date = datetime.strftime(search_date,DEFAULT_SERVER_DATETIME_FORMAT)
        issues = self.env['project.issue'].search([('date_action_last', operator, search_date)])
        return [('id', 'in', leads.ids)]
        
    age_issue = fields.Float(string = "Hours Since Created",compute="_cal_age_issue",store=False, search='_search_age_issue', help="Issue Age in Hours")
    age_since_update = fields.Float(string = "Hours Since Action",compute="_cal_update_age_issue",store=False, search='_search_update_age_issue', help="Issue Age Since las Update")