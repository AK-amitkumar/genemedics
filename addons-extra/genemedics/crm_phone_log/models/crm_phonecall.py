# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _

class crm_phonecall(osv.osv):
    """ Model for CRM phonecalls """
    _name = "crm.phonecall"
    _description = "Phonecall"
    _order = "id desc"
    _inherit = ['mail.thread']
    
    _columns = {
        'date_action_last': fields.datetime('Last Action', readonly=1),
        'date_action_next': fields.datetime('Next Action', readonly=1),
        'create_date': fields.datetime('Creation Date' , readonly=True),
        'team_id': fields.many2one('crm.case.section', 'Sales Team', \
                        select=True, help='Sales team to which Case belongs to.'),
        'user_id': fields.many2one('res.users', 'Responsible'),
        'partner_id': fields.many2one('res.partner', 'Contact'),
        'company_id': fields.many2one('res.company', 'Company'),
        'description': fields.text('Description'),
        'state': fields.selection(
            [('open', 'Confirmed'),
             ('cancel', 'Cancelled'),
             ('pending', 'Pending'),
             ('done', 'Held')
             ], string='Status', readonly=True, track_visibility='onchange',
            help='The status is set to Confirmed, when a case is created.\n'
                 'When the call is over, the status is set to Held.\n'
                 'If the callis not applicable anymore, the status can be set to Cancelled.'),
        'email_from': fields.char('Email', size=128, help="These people will receive email."),
        'date_open': fields.datetime('Opened', readonly=True),
        # phonecall fields
        'name': fields.char('Call Summary', required=True),
        'active': fields.boolean('Active', required=False),
        'duration': fields.float('Duration', help='Duration in minutes and seconds.'),
        'categ_id': fields.many2one('crm.case.categ', 'Category', \
                        domain="['|',('team_id','=',team_id),('team_id','=',False),\
                        ('object_id.model', '=', 'crm.phonecall')]"),
        'partner_phone': fields.char('Phone'),
        'partner_mobile': fields.char('Mobile'),
        'priority': fields.selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority'),
        'date_closed': fields.datetime('Closed', readonly=True),
        'date': fields.datetime('Date'),
        'opportunity_id': fields.many2one ('crm.lead', 'Lead/Opportunity'),
    }

    def _get_default_state(self, cr, uid, context=None):
        if context and context.get('default_state'):
            return context.get('default_state')
        return 'open'

    _defaults = {
        'date': fields.datetime.now,
        'priority': '1',
        'state':  _get_default_state,
        'user_id': lambda self, cr, uid, ctx: uid,
        'active': 1
    }

    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        values = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            values = {
                'partner_phone': partner.phone,
                'partner_mobile': partner.mobile,
            }
        return {'value': values}

    def write(self, cr, uid, ids, values, context=None):
        """ Override to add case management: open/close dates """
        if values.get('state'):
            if values.get('state') == 'done':
                values['date_closed'] = fields.datetime.now()
                self.compute_duration(cr, uid, ids, context=context)
            elif values.get('state') == 'open':
                values['date_open'] = fields.datetime.now()
                values['duration'] = 0.0
        return super(crm_phonecall, self).write(cr, uid, ids, values, context=context)

    def compute_duration(self, cr, uid, ids, context=None):
        for phonecall in self.browse(cr, uid, ids, context=context):
            if phonecall.duration <= 0:
                duration = datetime.now() - datetime.strptime(phonecall.date, DEFAULT_SERVER_DATETIME_FORMAT)
                values = {'duration': duration.seconds/float(60)}
                self.write(cr, uid, [phonecall.id], values, context=context)
        return True

    def schedule_another_phonecall(self, cr, uid, ids, schedule_time, call_summary, \
                    user_id=False, team_id=False, categ_id=False, action='schedule', context=None):
        """
        action :('schedule','Schedule a call'), ('log','Log a call')
        """
        model_data = self.pool.get('ir.model.data')
        phonecall_dict = {}
        if not categ_id:
            try:
                res_id = model_data._get_id(cr, uid, 'crm', 'categ_phone2')
                categ_id = model_data.browse(cr, uid, res_id, context=context).res_id
            except ValueError:
                pass
        for call in self.browse(cr, uid, ids, context=context):
            if not team_id:
                team_id = call.team_id and call.team_id.id or False
            if not user_id:
                user_id = call.user_id and call.user_id.id or False
            if not schedule_time:
                schedule_time = call.date
            vals = {
                    'name' : call_summary,
                    'user_id' : user_id or False,
                    'categ_id' : categ_id or False,
                    'description' : call.description or False,
                    'date' : schedule_time,
                    'team_id' : team_id or False,
                    'partner_id': call.partner_id and call.partner_id.id or False,
                    'partner_phone' : call.partner_phone,
                    'partner_mobile' : call.partner_mobile,
                    'priority': call.priority,
                    'opportunity_id': call.opportunity_id and call.opportunity_id.id or False,
            }
            new_id = self.create(cr, uid, vals, context=context)
            if action == 'log':
                self.write(cr, uid, [new_id], {'state': 'done'}, context=context)
            phonecall_dict[call.id] = new_id
        return phonecall_dict

    def _call_create_partner(self, cr, uid, phonecall, context=None):
        partner = self.pool.get('res.partner')
        partner_id = partner.create(cr, uid, {
                    'name': phonecall.name,
                    'user_id': phonecall.user_id.id,
                    'comment': phonecall.description,
                    'address': []
        })
        return partner_id

    def on_change_opportunity(self, cr, uid, ids, opportunity_id, context=None):
        values = {}
        if opportunity_id:
            opportunity = self.pool.get('crm.lead').browse(cr, uid, opportunity_id, context=context)
            values = {
                'team_id' : opportunity.team_id and opportunity.team_id.id or False,
                'partner_phone' : opportunity.phone,
                'partner_mobile' : opportunity.mobile,
                'partner_id' : opportunity.partner_id and opportunity.partner_id.id or False,
            }
        return {'value' : values}

    def _call_set_partner(self, cr, uid, ids, partner_id, context=None):
        write_res = self.write(cr, uid, ids, {'partner_id' : partner_id}, context=context)
        self._call_set_partner_send_note(cr, uid, ids, context)
        return write_res

    def _call_create_partner_address(self, cr, uid, phonecall, partner_id, context=None):
        address = self.pool.get('res.partner')
        return address.create(cr, uid, {
                    'parent_id': partner_id,
                    'name': phonecall.name,
                    'phone': phonecall.partner_phone,
        })

    def handle_partner_assignation(self, cr, uid, ids, action='create', partner_id=False, context=None):
        """
        Handle partner assignation during a lead conversion.
        if action is 'create', create new partner with contact and assign lead to new partner_id.
        otherwise assign lead to specified partner_id

        :param list ids: phonecalls ids to process
        :param string action: what has to be done regarding partners (create it, assign an existing one, or nothing)
        :param int partner_id: partner to assign if any
        :return dict: dictionary organized as followed: {lead_id: partner_assigned_id}
        """
        #TODO this is a duplication of the handle_partner_assignation method of crm_lead
        partner_ids = {}
        # If a partner_id is given, force this partner for all elements
        force_partner_id = partner_id
        for call in self.browse(cr, uid, ids, context=context):
            # If the action is set to 'create' and no partner_id is set, create a new one
            if action == 'create':
                partner_id = force_partner_id or self._call_create_partner(cr, uid, call, context=context)
                self._call_create_partner_address(cr, uid, call, partner_id, context=context)
            self._call_set_partner(cr, uid, [call.id], partner_id, context=context)
            partner_ids[call.id] = partner_id
        return partner_ids


    def redirect_phonecall_view(self, cr, uid, phonecall_id, context=None):
        model_data = self.pool.get('ir.model.data')
        # Select the view
        tree_view = model_data.get_object_reference(cr, uid, 'crm_phone_log', 'crm_case_phone_tree_view')
        form_view = model_data.get_object_reference(cr, uid, 'crm_phone_log', 'crm_case_phone_form_view')
        search_view = model_data.get_object_reference(cr, uid, 'crm_phone_log', 'view_crm_case_phonecalls_filter')
        value = {
                'name': _('Phone Call'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'crm.phonecall',
                'res_id' : int(phonecall_id),
                'views': [(form_view and form_view[1] or False, 'form'), (tree_view and tree_view[1] or False, 'tree'), (False, 'calendar')],
                'type': 'ir.actions.act_window',
                'search_view_id': search_view and search_view[1] or False,
        }
        return value

    def convert_opportunity(self, cr, uid, ids, opportunity_summary=False, partner_id=False, planned_revenue=0.0, probability=0.0, context=None):
        partner = self.pool.get('res.partner')
        opportunity = self.pool.get('crm.lead')
        opportunity_dict = {}
        default_contact = False
        for call in self.browse(cr, uid, ids, context=context):
            if not partner_id:
                partner_id = call.partner_id and call.partner_id.id or False
            if partner_id:
                address_id = partner.address_get(cr, uid, [partner_id])['default']
                if address_id:
                    default_contact = partner.browse(cr, uid, address_id, context=context)
            opportunity_id = opportunity.create(cr, uid, {
                            'name': opportunity_summary or call.name,
                            'planned_revenue': planned_revenue,
                            'probability': probability,
                            'partner_id': partner_id or False,
                            'mobile': default_contact and default_contact.mobile,
                            'team_id': call.team_id and call.team_id.id or False,
                            'description': call.description or False,
                            'priority': call.priority,
                            'type': 'opportunity',
                            'phone': call.partner_phone or False,
                            'email_from': default_contact and default_contact.email,
                        })
            vals = {
                'partner_id': partner_id,
                'opportunity_id': opportunity_id,
                'state': 'done',
            }
            self.write(cr, uid, [call.id], vals, context=context)
            opportunity_dict[call.id] = opportunity_id
        return opportunity_dict

    def action_make_meeting(self, cr, uid, ids, context=None):
        """
        Open meeting's calendar view to schedule a meeting on current phonecall.
        :return dict: dictionary value for created meeting view
        """
        partner_ids = []
        phonecall = self.browse(cr, uid, ids[0], context)
        if phonecall.partner_id and phonecall.partner_id.email:
            partner_ids.append(phonecall.partner_id.id)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'calendar', 'action_calendar_event', context)
        res['context'] = {
            'default_phonecall_id': phonecall.id,
            'default_partner_ids': partner_ids,
            'default_user_id': uid,
            'default_email_from': phonecall.email_from,
            'default_name': phonecall.name,
        }
        return res

    def action_button_convert2opportunity(self, cr, uid, ids, context=None):
        """
        Convert a phonecall into an opp and then redirect to the opp view.

        :param list ids: list of calls ids to convert (typically contains a single id)
        :return dict: containing view information
        """
        if len(ids) != 1:
            raise osv.except_osv(_('Warning!'),_('It\'s only possible to convert one phonecall at a time.'))

        opportunity_dict = self.convert_opportunity(cr, uid, ids, context=context)
        return self.pool.get('crm.lead').redirect_opportunity_view(cr, uid, opportunity_dict[ids[0]], context)

    # ----------------------------------------
    # OpenChatter
    # ----------------------------------------

    def _call_set_partner_send_note(self, cr, uid, ids, context=None):
        return self.message_post(cr, uid, ids, body=_("Partner has been <b>created</b>."), context=context)
    
    
class crm_case_categ(osv.osv):
    """ Category of Case """
    _name = "crm.case.categ"
    _description = "Category of Case"
    _columns = {
        'name': fields.char('Name', required=True, translate=True),
        'team_id': fields.many2one('crm.case.section', 'Sales Team'),
        'object_id': fields.many2one('ir.model', 'Object Name'),
    }

    def _find_object_id(self, cr, uid, context=None):
        """Finds id for case object"""
        context = context or {}
        object_id = context.get('object_id', False)
        ids = self.pool.get('ir.model').search(cr, uid, ['|', ('id', '=', object_id), ('model', '=', context.get('object_name', False))])
        return ids and ids[0] or False
    _defaults = {
        'object_id': _find_object_id
    }
    
class crm_case_section(osv.osv):
    _name = "crm.case.section"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Sales Teams"
    _order = "complete_name"
    _period_number = 5

    def get_full_name(self, cr, uid, ids, field_name, arg, context=None):
        return dict(self.name_get(cr, uid, ids, context=context))

    def __get_bar_values(self, cr, uid, obj, domain, read_fields, value_field, groupby_field, context=None):
        """ Generic method to generate data for bar chart values using SparklineBarWidget.
            This method performs obj.read_group(cr, uid, domain, read_fields, groupby_field).

            :param obj: the target model (i.e. crm_lead)
            :param domain: the domain applied to the read_group
            :param list read_fields: the list of fields to read in the read_group
            :param str value_field: the field used to compute the value of the bar slice
            :param str groupby_field: the fields used to group

            :return list section_result: a list of dicts: [
                                                {   'value': (int) bar_column_value,
                                                    'tootip': (str) bar_column_tooltip,
                                                }
                                            ]
        """
        month_begin = date.today().replace(day=1)
        section_result = [{
                          'value': 0,
                          'tooltip': tools.ustr((month_begin + relativedelta.relativedelta(months=-i)).strftime('%B %Y')),
                          } for i in range(self._period_number - 1, -1, -1)]
        group_obj = obj.read_group(cr, uid, domain, read_fields, groupby_field, context=context)
        pattern = tools.DEFAULT_SERVER_DATE_FORMAT if obj.fields_get(cr, uid, groupby_field)[groupby_field]['type'] == 'date' else tools.DEFAULT_SERVER_DATETIME_FORMAT
        for group in group_obj:
            group_begin_date = datetime.strptime(group['__domain'][0][2], pattern)
            month_delta = relativedelta.relativedelta(month_begin, group_begin_date)
            section_result[self._period_number - (month_delta.months + 1)] = {'value': group.get(value_field, 0), 'tooltip': group.get(groupby_field, 0)}
        return section_result

    _columns = {
        'name': fields.char('Sales Team', size=64, required=True, translate=True),
        'complete_name': fields.function(get_full_name, type='char', size=256, readonly=True, store=True),
        'code': fields.char('Code', size=8),
        'active': fields.boolean('Active', help="If the active field is set to "\
                        "false, it will allow you to hide the sales team without removing it."),
        'change_responsible': fields.boolean('Reassign Escalated', help="When escalating to this team override the salesman with the team leader."),
        'user_id': fields.many2one('res.users', 'Team Leader'),
        'member_ids': fields.many2many('res.users', 'sale_member_rel', 'section_id', 'member_id', 'Team Members'),
        'reply_to': fields.char('Reply-To', size=64, help="The email address put in the 'Reply-To' of all emails sent by Odoo about cases in this sales team"),
        'parent_id': fields.many2one('crm.case.section', 'Parent Team'),
        'child_ids': fields.one2many('crm.case.section', 'parent_id', 'Child Teams'),
        'note': fields.text('Description'),
        'working_hours': fields.float('Working Hours', digits=(16, 2)),
        'color': fields.integer('Color Index'),
    }

    _defaults = {
        'active': 1,
    }

    _sql_constraints = [
        ('code_uniq', 'unique (code)', 'The code of the sales team must be unique !')
    ]

    _constraints = [
        (osv.osv._check_recursion, 'Error ! You cannot create recursive Sales team.', ['parent_id'])
    ]

    def name_get(self, cr, uid, ids, context=None):
        """Overrides orm name_get method"""
        if not isinstance(ids, list):
            ids = [ids]
        res = []
        if not ids:
            return res
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context)

        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
