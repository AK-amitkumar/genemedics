


from openerp.osv import osv, fields
from lxml import etree


class helpdesk_issue(osv.osv):
    _inherit = "project.issue"
    
    def self_assign(self, cr, uid, ids, context={}):
        for iss in self.browse(cr,uid, ids, context):
            iss.write({'user_id':uid})
        return True

#     def fields_view_get(self, cr, uid, ids, view_id=None, view_type='form', toolbar=False,
#                     submenu=False):
#         res = super(helpdesk_issue, self).fields_view_get(cr, uid, ids, 
#             view_id=view_id, view_type=view_type, toolbar=toolbar,
#             submenu=submenu)
#         my_group_gid = self.env.ref(
#             'my_module.my_group').id
#         current_user_gids = self.env.user.groups_id.mapped('id')
#         if view_type == 'form':
#             if my_group_gid in current_user_gids:
#                 doc = etree.XML(res['arch'])
#                 the_fields = doc.xpath("//field[@name='my_field']")
#                 the_field = the_fields[0] if the_fields \
#                     else False
#                 the_field.set('readonly', '1')
#                 res['arch'] = etree.tostring(doc)
#         return res
helpdesk_issue()