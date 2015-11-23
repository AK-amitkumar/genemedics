# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models, tools, _ 
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT 
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


from __builtin__ import False

class crm_lead(models.Model):
    """ CRM Lead Case """
    _inherit = "crm.lead"

    @api.one
    def _cal_age_stage(self):
        
        delta = datetime.now() - datetime.strptime(self.date_last_stage_update, DEFAULT_SERVER_DATETIME_FORMAT)
        self.age_stage = int(delta.days)
        
        
    def _search_age_stage(self, operator, value):
        
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
        leads = self.env['crm.lead'].search([('date_last_stage_update', operator, search_date)])
        return [('id', 'in', leads.ids)]

    @api.one
    def _cal_age_lead(self):
        
        delta = datetime.now() - datetime.strptime(self.create_date, DEFAULT_SERVER_DATETIME_FORMAT)
        self.age_lead = int(delta.days)
        
    
    def _search_age_lead(self, operator, value):
        
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
    age_lead = fields.Integer(string = "Lead Age",compute="_cal_age_lead",store=False, search='_search_age_lead')
    age_stage = fields.Integer(string = "Stage Age" ,compute="_cal_age_stage",store=False, search='_search_age_stage')
    
    
    _order = 'create_date'
    
    @api.model
    def _user_groups(self, present_ids, domain, **kwargs):
        
        model_data = self.env['ir.model.data'].search( [('name','=','group_sale_salesman')])
        group = self.env['res.groups'].browse(model_data.res_id or [])
        users = group and group.users and group.users.name_get() or [] 
        return users, None

    @api.model
    def _stages(self, present_ids, domain, **kwargs):
        search_domain = self.env.context.get('stage_type_domain',[])
        stages =  self.env['crm.stage'].search(search_domain).name_get()
        return stages, None
    
    _group_by_full = {
                      'user_id':_user_groups,
                      'stage_id':_stages
                      }
    
    
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
        res['context']['default_user_id'] = lead.user_id.id or lead.env.uid
        return res
    
    @api.multi
    def action_schedule_activity(self):
        """
        Open meeting's calendar view to schedule meeting on current opportunity.
        :return dict: dictionary value for created Meeting view
        """
        res = self.env['ir.actions.act_window'].for_xml_id( 'crm_genemedics', 'action_calendar_event_genemedics')
        lead = self
        
        partner_ids = [self.user_id.partner_id.id]
        if lead.partner_id:
            partner_ids.append(lead.partner_id.id)
            
        name = (lead.next_activity_id and lead.next_activity_id.name) or False
                
        if name: 
            name = ('[%s] - %s ' %(name, lead.name))
        else: 
            name = lead.name
        
        res['context'] = {}
        
        res['context']['search_default_opportunity_id'] = (lead.id or False)
        res['context']['default_opportunity_id'] =  lead.id or False,
        res['context']['default_partner_id'] = lead.partner_id and lead.partner_id.id or False
        res['context']['default_partner_ids'] = partner_ids
        res['context']['default_team_id'] = lead.team_id and lead.team_id.id or False
        res['context']['default_name'] =  name
        res['context']['default_activity_id'] = lead.next_activity_id and lead.next_activity_id.id or False
        res['context']['default_activity_date'] = lead.date_action
        res['context']['default_user_id'] = lead.user_id.id or lead.env.uid
 #       context['default_all_day'] = True
     
                                   
        return res
    
    
    def retrieve_sales_dashboard(self, cr, uid, context=None):

        res = {
            'meeting': {
                'today': 0,
                'next_7_days': 0,
            },
            'all_meeting': {
                'today': 0,
                'next_7_days': 0,
            },
            'activity': {
                'today': 0,
                'overdue': 0,
                'next_7_days': 0,
            },
            'all_activity': {
                'today': 0,
                'overdue': 0,
                'next_7_days': 0,
            },
            'closing': {
                'today': 0,
                'overdue': 0,
                'next_7_days': 0,
            },
            'all_closing': {
                'today': 0,
                'overdue': 0,
                'next_7_days': 0,
            },
            'done': {
                'this_month': 0,
                'last_month': 0,
            },
            'all_done': {
                'this_month': 0,
                'last_month': 0,
            },
            'won': {
                'this_month': 0,
                'last_month': 0,
            },
            'all_won': {
                'this_month': 0,
                'last_month': 0,
            },
            'all_invoiced': {
            'this_month': 0,
            'last_month': 0,
            },
        
            'nb_opportunities': 0,
        }
        group_id = self.pool.get('ir.model.data').xmlid_to_res_id(cr,uid,'crm_genemedics.group_dashboard_all')
        group = self.pool.get('res.groups').browse(cr,uid,group_id,context=context)
        users =  group and group.users and group.users.ids or []
            
        if uid in users:
            is_dashboard_all = True
            res['manager_dash'] = True
        else:
            is_dashboard_all = False
            res['manager_dash'] = False
        
        all_opportunities = self.search_read(
                cr, uid,
                [],
                ['date_deadline', 'next_activity_id', 'date_action', 'date_closed', 'planned_revenue'], context=context)
        
        opportunities = self.search_read(
                cr, uid,
                [ ('user_id', '=', uid)],
                ['date_deadline', 'next_activity_id', 'date_action', 'date_closed', 'planned_revenue'], context=context)

            

        for opp in opportunities:

            # Expected closing
            if opp['date_deadline']:
                date_deadline = datetime.strptime(opp['date_deadline'], tools.DEFAULT_SERVER_DATE_FORMAT).date()

                if date_deadline == date.today():
                    res['closing']['today'] += 1
                if date_deadline >= date.today() and date_deadline <= date.today() + timedelta(days=7):
                    res['closing']['next_7_days'] += 1
                if date_deadline < date.today():
                    res['closing']['overdue'] += 1

            # Next activities
            if opp['next_activity_id'] and opp['date_action']:
                date_action = datetime.strptime(opp['date_action'], tools.DEFAULT_SERVER_DATE_FORMAT).date()

                if date_action == date.today():
                    res['activity']['today'] += 1
                if date_action >= date.today() and date_action <= date.today() + timedelta(days=7):
                    res['activity']['next_7_days'] += 1
                if date_action < date.today():
                    res['activity']['overdue'] += 1

            # Won in Opportunities
            if opp['date_closed']:
                date_closed = datetime.strptime(opp['date_closed'], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()

                if date_closed <= date.today() and date_closed >= date.today().replace(day=1):
                    if opp['planned_revenue']:
                        res['won']['this_month'] += opp['planned_revenue']
                elif date_closed < date.today().replace(day=1) and date_closed >= date.today().replace(day=1) - relativedelta(months=+1):
                    if opp['planned_revenue']:
                        res['won']['last_month'] += opp['planned_revenue']
                            
                            
        for opp in all_opportunities:
            # Expected closing
            if opp['date_deadline']:
                date_deadline = datetime.strptime(opp['date_deadline'], tools.DEFAULT_SERVER_DATE_FORMAT).date()

                if date_deadline == date.today():
                    res['all_closing']['today'] += 1
                if date_deadline >= date.today() and date_deadline <= date.today() + timedelta(days=7):
                    res['all_closing']['next_7_days'] += 1
                if date_deadline < date.today():
                    res['all_closing']['overdue'] += 1

            # Next activities
            if opp['next_activity_id'] and opp['date_action']:
                date_action = datetime.strptime(opp['date_action'], tools.DEFAULT_SERVER_DATE_FORMAT).date()

                if date_action == date.today():
                    res['all_activity']['today'] += 1
                if date_action >= date.today() and date_action <= date.today() + timedelta(days=7):
                    res['all_activity']['next_7_days'] += 1
                if date_action < date.today():
                    res['all_activity']['overdue'] += 1

            # Won in Opportunities
            if opp['date_closed']:
                date_closed = datetime.strptime(opp['date_closed'], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()

                if date_closed <= date.today() and date_closed >= date.today().replace(day=1):
                    if opp['planned_revenue']:
                        res['all_won']['this_month'] += opp['planned_revenue']
                elif date_closed < date.today().replace(day=1) and date_closed >= date.today().replace(day=1) - relativedelta(months=+1):
                    if opp['planned_revenue']:
                        res['all_won']['last_month'] += opp['planned_revenue']
        

        # crm.activity is a very messy model so we need to do that in order to retrieve the actions done.
        if is_dashboard_all: cr.execute("""
            SELECT
                m.id,
                m.subtype_id,
                m.date,
                l.user_id,
                l.type
            FROM
                "mail_message" m
            LEFT JOIN
                "crm_lead" l
            ON
                (m.res_id = l.id)
            INNER JOIN
                "crm_activity" a
            ON
                (m.subtype_id = a.subtype_id)
            WHERE
                (m.model = 'crm.lead') AND (l.user_id = %s) 
        """, (uid,))
        
        activites_done = cr.dictfetchall()

        for act in activites_done:
            if act['date']:
                date_act = datetime.strptime(act['date'], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
                if date_act <= date.today() and date_act >= date.today().replace(day=1):
                        res['done']['this_month'] += 1
                elif date_act < date.today().replace(day=1) and date_act >= date.today().replace(day=1) - relativedelta(months=+1):
                    res['done']['last_month'] += 1

        # Meetings
        min_date = datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        max_date = (datetime.now() + timedelta(days=8)).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        meetings_domain = [
            ('start', '>=', min_date),
            ('start', '<=', max_date)
        ]
        # We need to add 'mymeetings' in the context for the search to be correct.
        meetings = self.pool.get('calendar.event').search_read(cr, uid, meetings_domain, ['start'], context=context.update({'mymeetings': 1}) if context else {'mymeetings': 1})
        for meeting in meetings:
            if meeting['start']:
                start = datetime.strptime(meeting['start'], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()

                if start == date.today():
                    res['meeting']['today'] += 1
                if start >= date.today() and start <= date.today() + timedelta(days=7):
                    res['meeting']['next_7_days'] += 1

        res['nb_opportunities'] = len(opportunities)

        user = self.pool('res.users').browse(cr, uid, uid, context=context)
        res['done']['target'] = user.target_sales_done
        res['won']['target'] = user.target_sales_won

        res['currency_id'] = user.company_id.currency_id.id
        
        cr.execute("""
            SELECT
                m.id,
                m.subtype_id,
                m.date,
                l.user_id,
                l.type
            FROM
                "mail_message" m
            LEFT JOIN
                "crm_lead" l
            ON
                (m.res_id = l.id)
            INNER JOIN
                "crm_activity" a
            ON
                (m.subtype_id = a.subtype_id)
            WHERE
                (m.model = 'crm.lead') 
        """)
            
        activites_done = cr.dictfetchall()

        for act in activites_done:
            if act['date']:
                date_act = datetime.strptime(act['date'], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
                if date_act <= date.today() and date_act >= date.today().replace(day=1):
                    res['all_done']['this_month'] += 1
                elif date_act < date.today().replace(day=1) and date_act >= date.today().replace(day=1) - relativedelta(months=+1):
                    res['all_done']['last_month'] += 1

        # Meetings
        min_date = datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        max_date = (datetime.now() + timedelta(days=8)).strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        meetings_domain = [
            ('start', '>=', min_date),
            ('start', '<=', max_date)
        ]
        # We need to add 'mymeetings' in the context for the search to be correct.
        meetings = self.pool.get('calendar.event').search_read(cr, uid, meetings_domain, ['start'], context=context.update({'mymeetings': 1}) if context else {'mymeetings': 1})
        for meeting in meetings:
            if meeting['start']:
                start = datetime.strptime(meeting['start'], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()

                if start == date.today():
                    res['all_meeting']['today'] += 1
                if start >= date.today() and start <= date.today() + timedelta(days=7):
                    res['all_meeting']['next_7_days'] += 1

        res['nb_opportunities'] = len(opportunities)

        user = self.pool('res.users').browse(cr, uid, uid, context=context)
        res['all_done']['target'] = user.target_sales_done
        res['all_won']['target'] = user.target_sales_won

        res['currency_id'] = user.company_id.currency_id.id
        
        
        all_account_invoice_domain = [
            ('state', 'in', ['open', 'paid']),
            ('date', '>=', date.today().replace(day=1) - relativedelta(months=+1))
        ]

        invoice_ids = self.pool.get('account.invoice').search_read(cr, uid, all_account_invoice_domain, ['date', 'amount_untaxed_signed'], context=context)
        for inv in invoice_ids:
            if inv['date']:
                inv_date = datetime.strptime(inv['date'], tools.DEFAULT_SERVER_DATE_FORMAT).date()
                if inv_date <= date.today() and inv_date >= date.today().replace(day=1):
                    res['all_invoiced']['this_month'] += inv['amount_untaxed_signed']
                elif inv_date < date.today().replace(day=1) and inv_date >= date.today().replace(day=1) - relativedelta(months=+1):
                    res['all_invoiced']['last_month'] += inv['amount_untaxed_signed']
        
        group_id = self.pool.get('ir.model.data').xmlid_to_res_id(cr,uid,'base.group_sale_salesman')
        group = self.pool.get('res.groups').browse(cr,uid,group_id,context=context)
        users =  group and group.users and group.users.ids or []
        invoiced_target = 0.0
        won_target = 0.0
        done_target = 0.0
        
        for user in self.pool('res.users').browse(cr, uid, users, context=context):
            invoiced_target += user.target_sales_invoiced
            won_target += user.target_sales_won
            done_target += user.target_sales_done
            
        res['all_invoiced']['target'] = invoiced_target
        res['all_won']['target'] = won_target
        res['all_done']['target'] = done_target
        

        return res
    
    def action_all_pipeline(self, cr, uid, context=None):
        IrModelData = self.pool['ir.model.data']
        action = IrModelData.xmlid_to_object(cr, uid, 'crm_genemedics.crm_lead_all_leads_genemedics').read(['name', 'help', 'res_model', 'target', 'domain', 'context', 'type', 'search_view_id'])
        if not action:
            action = {}
        else:
            action = action[0]

        user_team_id = self.pool['res.users'].browse(cr, uid, uid, context=context).sale_team_id.id
        if not user_team_id:
            user_team_id = self.search(cr, uid, [], context=context, limit=1)
            user_team_id = user_team_id and user_team_id[0] or False
            action['help'] = """<p class='oe_view_nocontent_create'>Click here to add new opportunities</p><p>
    Looks like you are not a member of a sales team. You should add yourself
    as a member of one of the sales team.
</p>"""
            if user_team_id:
                action['help'] += "<p>As you don't belong to any sales team, Odoo opens the first one by default.</p>"

        action_context = eval(action['context'], {'uid': uid})
        if user_team_id:
            action_context.update({
                'default_team_id': user_team_id,
                'search_default_team_id': user_team_id
            })

        tree_view_id = IrModelData.xmlid_to_res_id(cr, uid, 'crm_genemedics.crm_case_tree_view_oppor_genemedics')
        form_view_id = IrModelData.xmlid_to_res_id(cr, uid, 'crm.crm_case_form_view_oppor')
        kanb_view_id = IrModelData.xmlid_to_res_id(cr, uid, 'crm.crm_case_kanban_view_leads')
        action.update({
            'views': [
                [kanb_view_id, 'kanban'],
                [tree_view_id, 'tree'],
                [form_view_id, 'form'],
                [False, 'graph'],
                [False, 'calendar'],
                [False, 'pivot']
            ],
            'context': action_context,
        })
        return action