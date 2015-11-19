from openerp import api, models, fields



class email_wizard_view(models.TransientModel):
    
    _name = 'email.wizard.view'
    
   
    txt_temp = fields.Text('Text')
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(email_wizard_view, self).default_get(cr, uid, fields, context=context)
        mail = self.pool.get('mail.template').browse(cr, uid, context['active_id'], context=context)
        
        res.update({'txt_temp': mail.body_html})
        return res
    
    
    def return_to_form(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wizard_obj = self.pool.get('email.wizard.view').browse(cr,uid,ids)
        txt_temp=wizard_obj.txt_temp
        mail_obj = self.pool.get('mail.template')
        mail_ids = context['active_ids']
        
        if context.get('active_id'):
            active_id=context.get('active_id')
            mail_obj.write(cr, uid, active_id,{'body_html':txt_temp})
        return {'type': 'ir.actions.act_window_close'}