# -*- coding: utf-8 -*-


from datetime import datetime
from openerp import models, fields, api, osv, exceptions
from openerp.tools import html2plaintext
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class priority(models.Model):
	_name = 'help_support.priority'
	_description = "Helpdesk Priority"
	name = fields.Char(string="Title",required=True)
	description = fields.Text() 

	@api.one
	def copy(self, default=None):
        	default = dict(default or {})

        	copied_count = self.search_count(
            		[('name', '=like', u"Copy of {}%".format(self.name))])
        	if not copied_count:
            		new_name = u"Copy of {}".format(self.name)
        	else:
            		new_name = u"Copy of {} ({})".format(self.name, copied_count)

        	default['name'] = new_name
        	return super(Course, self).copy(default)


class hsupport(models.Model):
	_name = 'help_support.hsupport'
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_description = "Helpdesk"	
	name = fields.Char(string="Title")
	description = fields.Html()
	email = fields.Char(string="Email")
	partner_id = fields.Many2one('res.partner', ondelete='set null', string = 'Customer', track_visibility='onchange')
	date_ = fields.Date()
	active = fields.Boolean(default=True)
	priority_id = fields.Many2one('help_support.priority', ondelete='cascade', string="Priority")
	state = fields.Selection([('open', "Open"),('pending', "Pending"),('solved', "Solved"),], default='open',track_visibility='onchange')
	color = fields.Integer()
	create_date = fields.Datetime(string='Created Date', readonly=True)
	write_date = fields.Datetime(string='Write Date', readonly=True)
	days_since_creation = fields.Integer(string="Days since creation ticket", compute='_count_statistics_days')
	closed_date = fields.Datetime(string='Closed Date', readonly=True)
	pending_date = fields.Datetime(string='Pending Date', readonly=True)
	re_open_date = fields.Datetime(string='Re-open Date', readonly=True)
	inactivity_days = fields.Integer(string="Inactivity days", compute='_count_statistics_days')
    	id_ = fields.Integer(string ="Id", readonly=True)
	responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsible", index=True, read=['help_support.group_manager'], track_visibility='onchange')
	_order= 'create_date desc'

	@api.one
    	def action_open(self):
        	self.state = 'open'
		self.re_open_date = fields.datetime.now()

    	@api.one
    	def action_pending(self):
        	self.state = 'pending'

    	@api.one
    	def action_solved(self):
        	self.state = 'solved'
		self.closed_date = fields.datetime.now()

	@api.one
	@api.depends('write_date','create_date')
	def _count_statistics_days(self):
		if self.write_date:
			counted_days = datetime.today() - datetime.strptime(self.write_date, DEFAULT_SERVER_DATETIME_FORMAT)
			self.inactivity_days=counted_days.days
		if self.create_date:
			counted_since_creation_days = datetime.today() - datetime.strptime(self.create_date, DEFAULT_SERVER_DATETIME_FORMAT)
			self.days_since_creation=counted_since_creation_days.days

	
	
	def create(self, cr, uid, vals, context=None):
		vals['create_date'] = fields.datetime.now()
#		vals['ticket_id'] = self.pool.get('ir.sequence').get(cr, uid, 'sequence_number')
		vals['id_'] = self.pool.get('ir.sequence').get(cr, uid, 'sequence_code')
		return super(hsupport, self).create(cr, uid, vals, context)

	
	def write(self, cr, uid, ids, vals, context=None):
        	vals['write_date'] = fields.datetime.now()
		if vals.get('state'):
            		if vals.get('state') in ['pending'] and not vals.get('pending_date'):
                		vals['pending_date'] = fields.datetime.now()
            		elif vals.get('state') == 'solved' and not vals.get('closed_date'):
                		vals['closed_date'] = fields.datetime.now()
            		elif vals.get('state') == 'open' and not vals.get('re_open_date'):
                		vals['re_open_date'] = fields.datetime.now()
		return super(hsupport, self).write(cr, uid, ids, vals, context)
	
	
	def message_new(self, cr, uid, msg_dict, custom_values=None, context=None):
        	"""Called by ``message_process`` when a new message is received
           for a given thread model, if the message did not belong to
           an existing thread.
           The default behavior is to create a new record of the corresponding
           model (based on some very basic info extracted from the message).
           Additional behavior may be implemented by overriding this method.

           :param dict msg_dict: a map containing the email details and
                                 attachments. See ``message_process`` and
                                ``mail.message.parse`` for details.
           :param dict custom_values: optional dictionary of additional
                                      field values to pass to create()
                                      when creating the new thread record.
                                      Be careful, these values may override
                                      any other values coming from the message.
           :param dict context: if a ``thread_model`` value is present
                                in the context, its value will be used
                                to determine the model of the record
                                to create (instead of the current model).
           :rtype: int
           :return: the id of the newly created thread object
        	"""
        	if context is None:
            		context = {}
	        data = {}
        	if isinstance(custom_values, dict):
        	    data = custom_values.copy()
        	model = context.get('thread_model') or self._name
        	model_pool = self.pool[model]
        	fields = model_pool.fields_get(cr, uid, context=context)
        	if 'name' in fields and not data.get('name'):
        	    data['name'] = msg_dict.get('subject', '')
        	    data['email'] = msg_dict.get('from')
        	    data['description'] = msg_dict.get('body')
        	    data['partner_id'] = msg_dict.get('author_id', False)
        	res_id = model_pool.create(cr, uid, data, context=context)
        	return res_id






	
