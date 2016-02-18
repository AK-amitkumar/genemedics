# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, models, fields
import datetime
import openerp
import re
from openerp.http import request
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _

skip_models_list = ['ir.property', 'ir.model.data', 'ir.module.module']


def is_module_installed(env, module_name):
    """ Check if an Odoo addon is installed.

    :param module_name: name of the addon
    """
    # the registry maintains a set of fully loaded modules so we can
    # lookup for our module there
    return module_name in env.registry._init_modules

create_original = models.BaseModel.create


@openerp.api.model
@openerp.api.returns('self', lambda value: value.id)
def create(self, vals):
    record_id = create_original(self, vals)
    if is_module_installed(self.env, 'popup_reminder') and self._name != 'bus.bus':
        popup_obj = self.pool['popup.reminder']
        model_ids = popup_obj.search(self._cr, self._uid, [('model_id','=', self._name)])
        if model_ids or self._name == "popup.reminder":
            count = popup_obj.set_notification(self._cr, self._uid, True)
            self.pool['bus.bus'].sendmany(self._cr, self._uid, [[(self._cr.dbname, 'popup.reminder'), str(count)]])
    return record_id
models.BaseModel.create = create


write_original = models.BaseModel.write


@openerp.api.multi
def write(self, vals):
    result = write_original(self, vals)
    context = dict(self._context)
    if context is None:
        context = {}
    if context.get('_force_unlink', False) or self._name in skip_models_list:
        return result
    if is_module_installed(self.env, 'popup_reminder') and self._name != 'bus.bus':
        popup_obj = self.pool['popup.reminder']
        model_ids = popup_obj.search(self._cr, self._uid, [('model_id','=', self._name)])
        if model_ids or self._name == "popup.reminder":
            count = popup_obj.set_notification(self._cr, self._uid, True)
            self.pool['bus.bus'].sendmany(self._cr, self._uid, [[(self._cr.dbname, 'popup.reminder'), str(count)]])
    return result
models.BaseModel.write = write


unlink_original = models.BaseModel.unlink


@openerp.api.multi
def unlink(self):
    context = dict(self._context)
    if context is None:
        context = {}
    if context.get('_force_unlink', False) or self._name in skip_models_list:
        return unlink_original(self)
    if is_module_installed(self.env, 'popup_reminder') and self._name != 'bus.bus':
        popup_obj = self.pool['popup.reminder']
        model_ids = popup_obj.search(self._cr, self._uid, [('model_id','=', str(self._name))])
        if model_ids or self._name == "popup.reminder":
            count = popup_obj.set_notification(self._cr, self._uid, True)
            self.pool['bus.bus'].sendmany(self._cr, self._uid, [[(self._cr.dbname, 'popup.reminder'), str(count)]])
    return unlink_original(self)
models.BaseModel.unlink = unlink


class Controller(openerp.addons.bus.controllers.main.BusController):
     # override to add channels
    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            registry, cr, uid, context = request.registry, request.cr, request.session.uid, request.context
            channels.append((request.db,'popup.reminder'))
        poll = super(Controller, self)._poll(dbname, channels, last, options)
        return poll


class popup_reminder(models.Model):
    _name = 'popup.reminder'

    def get_model_name(self, cr, uid, data, context=None):
        data_ids = self.search(cr, uid, [('name','=', data)])
        model_list = []
        if data_ids:
            model_name = self.browse(cr, uid, data_ids[0]).model_id.name
            model_name1 = self.browse(cr, uid, data_ids[0]).model_id.model
            model_list.append(model_name)
            model_list.append(model_name1)
        return model_list

    def get_form_data(self, cr, uid, data, context=None):
        data_ids = self.search(cr, uid, [('name','=', data)])
        model_name = ''
        if data_ids:
            model_name = self.browse(cr, uid, data_ids[0]).model_id.model
        return model_name

    def get_color_name(self, cr, uid, key, context=None):
        res = {}
        reminder_id = self.search(cr, uid, [('name','=', key)])
        if reminder_id:
            color_name = self.browse(cr, uid, reminder_id[0]).color
            res.update({str(key): color_name})
        return res

    def get_unique_id(self, cr, uid, context=None):
        res = {}
        reminder_ids = self.search(cr, uid, [], context=context)
        for data in self.browse(cr, uid, reminder_ids, context=context):
            unique_id = 'ui' + str(data.id) + str(data.model_id.id) + str(data.field_id.id)
            res.update({str(data.name): unique_id})
        return res

    def set_record_header(self, cr, uid, context=None):
        reminder_ids = self.search(cr, uid, [], context=context)
        res = {}
        for data in self.browse(cr, uid, reminder_ids, context=context):
            field_res = {}
            field_label = []
            for display_data in data.popup_field_ids:
                field_res.update({str(display_data.name):str(display_data.field_description)})
            field_label.append(field_res)
            res.update({str(data.name): field_label})
        return res

    def set_notification(self, cr, uid, count=False, context=None):
        res = {}
        reminder_ids = self.search(cr, uid, [], context=context)
        today_date = datetime.date.today()
        cur_month_first_date = today_date + relativedelta(day=1)
        cur_month_last_date = today_date + relativedelta(day=1, months= +1, days= -1)
        next_month_first_date = today_date + relativedelta(day=1, months= +1)
        next_month_last_date = today_date + relativedelta(day=1, months= +2, days= -1)
        next_month = datetime.date.today() + relativedelta(months=1)
        for data in self.browse(cr, uid, reminder_ids, context=context):
            today_date = datetime.date.today()
            data_ids = []
            model_obj = self.pool.get(data.model_id.model)
            if data.search_option == 'current_month':
                if data.from_today:
                    if data.field_id.ttype in ['datetime']:
                        try:
                            cur_month_last_date = datetime.datetime.strptime(str(cur_month_last_date), DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        except:
                            cur_month_last_date = datetime.datetime.strptime(str(cur_month_last_date), '%Y-%m-%d').strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        today_date = today_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    data_ids = model_obj.search(cr, uid, [(data.field_id.name, '>=', today_date),
                                                         (data.field_id.name, '<=', cur_month_last_date)])
                else:
                    if data.field_id.ttype in ['datetime']:
                        try:
                            cur_month_last_date = datetime.datetime.strptime(str(cur_month_last_date),'%Y-%m-%d %H:%M:%S').strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        except:
                            cur_month_last_date = datetime.datetime.strptime(str(cur_month_last_date),'%Y-%m-%d').strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        try:
                            cur_month_first_date = datetime.datetime.strptime(str(cur_month_first_date),'%Y-%m-%d %H:%M:%S').strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        except:
                            cur_month_first_date = datetime.datetime.strptime(str(cur_month_first_date),'%Y-%m-%d').strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    data_ids = model_obj.search(cr, uid, [(data.field_id.name, '>=', cur_month_first_date),
                                                         (data.field_id.name, '<=', cur_month_last_date)])
            if data.search_option == 'next_month':
                if data.field_id.ttype in ['datetime']:
                    next_month_first_date = next_month_first_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    next_month_last_date = next_month_last_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                data_ids = model_obj.search(cr, uid, [(data.field_id.name, '>=', next_month_first_date),
                                                     (data.field_id.name, '<=', next_month_last_date)])
            if data.search_option == 'days':
                next_date = False
                if data.field_id.ttype in ['datetime']:
                    today_date = today_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                    next_date = datetime.date.today()+datetime.timedelta(days=data.duration_in_days)
                    next_date = next_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                if not next_date:
                    next_date = datetime.date.today()+datetime.timedelta(days=data.duration_in_days)
                    next_date = next_date.strftime(DEFAULT_SERVER_DATE_FORMAT)
                data_ids = model_obj.search(cr, uid, [(data.field_id.name, '>=', today_date),
                                                     (data.field_id.name, '<=', next_date)])
            if data.search_option == 'today':
                if data.field_id.ttype in ['datetime']:
                    today_date = today_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                data_ids = model_obj.search(cr, uid, [(data.field_id.name, '>=', today_date),
                                                     (data.field_id.name, '<=', today_date)])
            read_data = []
            field_label = []
            field_res = {}
            for display_data in data.popup_field_ids:
                read_data.append(str(display_data.name))
                field_res.update({str(display_data.name):str(display_data.field_description)})
            field_label.append(field_res)
            model_data = model_obj.read(cr, uid, data_ids, read_data, context=context)
            modle_line_data = list(model_data)
            for model in modle_line_data:
                if data.model_id.model == 'mail.message' and model['model'] == "project.issue":
                    plain_text = re.compile(r'<.*?>').sub('',model['body'])
                    model['body'] = re.compile(r'&.*?;').sub('',plain_text)
                    user_id = self.pool.get('res.users').browse(cr, uid, uid).partner_id.id
                    mail_id = self.pool.get('mail.followers').search(cr, uid, [('partner_id','=',user_id),('res_model','=',model['model']),
                                                                   ('res_id','=',model['res_id'])])
                    if mail_id :
                        if model['record_for_notification_ids'] :
                            for notification_rec in self.pool.get('notification.msg').browse(cr,uid,model['record_for_notification_ids']):
                                if notification_rec.partner_id.id == user_id and notification_rec.notification_check == False:
                                    model['display_read_button'] = True
                                elif notification_rec.partner_id.id == user_id and notification_rec.notification_check:
                                    model['display_read_button'] = False
                                else : 
                                    model['display_read_button'] = False
                    if not mail_id :
                        model_data.remove(model)
                if data.model_id.model == 'mail.message' and model['model'] != "project.issue":
                    model_data.remove(model)
                field_label.append(model)
            res.update({str(data.name): model_data})
        if count:
            total = 0
            for k,v in res.iteritems():
                total += len(v)
            return total
        return res

    name = fields.Char('Name', size=128)
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    field_id = fields.Many2one('ir.model.fields', 'Fields', domain="[('model_id', '=', model_id),('ttype','in',['date','datetime'])]")
    popup_field_ids = fields.Many2many('ir.model.fields', 'popup_ir_model_field', 'field_id', 'popup_field_id', 'Display Fields', domain="[('model_id', '=', model_id)]")
    search_option = fields.Selection([('days', 'Days'), ('today', 'Today'), ('current_month', 'Current Month'), ('next_month', 'Next Month')], 'Search Option')
    duration_in_days = fields.Integer('Days')
    color = fields.Char('Color', size=64)
    from_today = fields.Boolean('From Today')

class notification_msg(models.Model):

    _name = 'notification.msg'

    partner_id = fields.Many2one('res.partner', 'Partner')
    message_id = fields.Many2one('mail.message', 'Message')
    notification_check = fields.Boolean('Notification check')

    def update_notification_msg(self, cr, uid, data, context=None):
        partner_id =  self.pool.get('res.users').browse(cr, uid, uid).partner_id.id
        notification_msg_id = self.search(cr, uid, [('partner_id','=', partner_id),('message_id','=',int(data))])
        self.write(cr,uid,notification_msg_id,{'notification_check':True})
        return True

class Message(models.Model):

    _inherit = 'mail.message'

    record_for_notification_ids = fields.One2many('notification.msg', 'message_id', string='Tracking values')

    @api.model
    def create(self, vals):
        res = super(Message, self).create(vals)
        notification_list = []
        if res.model == 'project.issue':
            project_rec = self.env['project.issue'].browse(res.res_id)
            for partner_rec in project_rec.message_follower_ids:
                if partner_rec.partner_id.id == res.author_id.id :
                    notification_list.append((0,0,{'message_id': res.id, 'partner_id': res.author_id.id,'notification_check':True}))
                else : 
                    notification_list.append((0,0,{'message_id': res.id, 'partner_id': partner_rec.partner_id.id}))
            res.write({'record_for_notification_ids': notification_list})
        return res

