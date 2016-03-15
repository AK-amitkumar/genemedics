# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Till Today Serpent Consulting Services PVT LTD (<http://www.serpentcs.com>)
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

from openerp.osv import fields, osv
from datetime import datetime


class project_issue(osv.osv):

    _inherit = 'project.issue'

    _columns = {
        'open_state_start_time': fields.datetime('Open state Start Time'),
    }

    def write(self, cr, uid, ids, vals, context=None):
        open_id = self.pool.get('project.task.type').search(cr, uid, [('name', '=', 'Open')], limit=1, context=context)
        if open_id and vals.get('stage_id') == open_id[0]:
            vals.update({'open_state_start_time': datetime.now()}) 
        return super(project_issue, self).write(cr, uid, ids, vals, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
