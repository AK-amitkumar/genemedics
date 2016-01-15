# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp.osv import fields, osv


class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def _count_email(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            res[partner.id] = len(self.pool.get("mail.message").search(cr,uid, ['|', ('author_id', '=', partner.id) ,('partner_ids', 'in', [partner.id])]))
                               
        return res
    
    def _count_calls(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for partner in self.browse(cr, uid, ids, context=context):
            res[partner.id] = len(self.pool.get("crm.phonecall").search(cr,uid, [('partner_id', '=', partner.id)]))
        return res

    _columns={
              'phonecall_ids' : fields.one2many("crm.phonecall", "partner_id", "Phonecalls"),
              'emails_count': fields.function(_count_email, type='integer', string="E-mails count"),
              'calls_count': fields.function(_count_calls, type='integer', string="Calls count"),
              }
res_partner()