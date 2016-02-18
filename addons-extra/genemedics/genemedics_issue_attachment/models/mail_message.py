# -*- coding: utf-8 -*-
# © 2016-Today Serpent Consulting Services Pvt. Ltd.
#    (<http://www.serpentcs.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from openerp import models,fields, api, _
import tempfile
from os import chdir
import base64
import html2text


class Message(models.Model):

    _inherit = 'mail.message'

    @api.model
    def create(self, vals):
        res = super(Message, self).create(vals)
        if self._context.get('default_model') == 'project.issue':
            temp_path = tempfile.gettempdir()
            chdir(temp_path)
            temp_xls = temp_path + '/email.txt'
            fp = open(temp_xls, 'wb+')
            for msg in res:
                plain_text = html2text.html2text(msg.body)
                fp.write(plain_text.encode('utf8') + '\n')
            fp.close()
            pfilecontents = open(temp_xls, 'rb+').read()
            result = base64.b64encode(pfilecontents)
            attachment_data = {
                            'name': 'Email Content.txt',
                            'datas_fname': 'Email Content',
                            'datas': result,
                            'res_model': 'project.issue',
                            'type': 'binary',
                            'res_id': res.res_id,
                        }
            self.env['ir.attachment'].create(attachment_data)
        return res