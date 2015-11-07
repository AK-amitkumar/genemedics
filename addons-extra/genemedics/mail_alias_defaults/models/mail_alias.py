# -*- coding: utf-8 -*-
#  See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api,exceptions, _

class mail_alias(models.Model):
    
    _inherits = 'mail.alias'
    
    # Fake fields used to implement the placeholder assistant
    model_object_field = fields.Many2one('ir.model.fields', string="Field",
                                         help="Select target field from the related document model.\n"
                                              "If it is a relationship field you will be able to select "
                                              " the ID values of record.")

