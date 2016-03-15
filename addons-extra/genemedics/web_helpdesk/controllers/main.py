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

from datetime import datetime
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class helpDesk(http.Controller):

    @http.route(['/notification-data'], type='json', auth='public', website=True)
    def notification_data(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        project_issue_obj = pool['project.issue']
        project_project_obj = pool['project.project']
        project_project_ids = project_project_obj.search(cr, SUPERUSER_ID, [('name', '=', 'Helpdesk')], limit=1, context=context)
        open_id = pool['project.task.type'].search(cr, SUPERUSER_ID, [('name', '=', 'Open')], limit=1, context=context)
        project_issue_ids = project_issue_obj.search(cr, SUPERUSER_ID, [('project_id', 'in', project_project_ids), ('stage_id', 'in', open_id)], context=context)
        
        flag = False
        res = {}
        records = []
        
        for issue in project_issue_obj.browse(cr, SUPERUSER_ID, project_issue_ids,context=context):
            if ((datetime.now() - (datetime.strptime(issue.open_state_start_time, DEFAULT_SERVER_DATETIME_FORMAT))).total_seconds()) / 60 >= 15:
                records.append(issue)
                flag = True
        html_data = request.website._render('web_helpdesk.notification_data', {'records': records})
        return {'html_data': html_data, 'flag': flag}

    @http.route(['/helpDesk'], type='http', auth='public', website=True)
    def helpDesk(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        project_task_obj = pool['project.task.type']
        project_issue_obj = pool['project.issue']
        project_project_obj = pool['project.project']
        project_project_ids = project_project_obj.search(cr, SUPERUSER_ID, [('name', '=', 'Helpdesk')], limit=1, context=context)
        task_list = []
        data = {'admin_panel': False}
        if project_project_ids:
            project_project_records = project_project_obj.browse(cr, SUPERUSER_ID, project_project_ids, context=context)
            for task in project_project_records.type_ids:
                domain = [('stage_id', '=', task.id), ('project_id', '=', project_project_ids[0])]
                if task.name == 'New':
                    domain.append(('user_id', '=', False))
                else:
                    domain.append(('user_id', '=', uid))
                total_records = len(project_issue_obj.search(cr, SUPERUSER_ID, domain, context=context))
                if (task.name == 'HIGH PRIORITY' or task.name == 'Need Assistance') and total_records == 0:
                    continue
                else:
                    task_list.append({'id': task.id, 'name': task.name, 'len': total_records})
        data.update({'project_tasks': task_list})
        help_desk_admin_group_id = request.registry['ir.model.data'].get_object_reference(cr, SUPERUSER_ID, 'web_helpdesk', 'help_desk_admin')[1]
        admin_users = request.registry['res.groups'].browse(cr, SUPERUSER_ID, help_desk_admin_group_id, context=context).users.ids
        if uid in admin_users:
            data.update({'admin_panel': True})
        return request.render('web_helpdesk.help_desk', data)

    @http.route(['/employee-data'], type='json', auth='public', website=True)
    def employee_data(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        ir_model_data_obj = request.registry['ir.model.data']
        res_group_obj = request.registry['res.groups']
        project_issue_obj = pool['project.issue']
        res_users_obj = pool['res.users']
        project_project_obj = pool['project.project']
        help_desk_admin_group_id = ir_model_data_obj.get_object_reference(cr, SUPERUSER_ID, 'web_helpdesk', 'help_desk_admin')[1]
        admin_users = res_group_obj.browse(cr, SUPERUSER_ID, help_desk_admin_group_id, context=context).users.ids
        admin_users.remove(uid)
        help_desk_employee_group_id = ir_model_data_obj.get_object_reference(cr, SUPERUSER_ID, 'web_helpdesk', 'help_desk_employee')[1]
        employee_users = res_group_obj.browse(cr, SUPERUSER_ID, help_desk_employee_group_id, context=context).users.ids
        users = admin_users + employee_users
        project_project_ids = project_project_obj.search(cr, SUPERUSER_ID, [('name', '=', 'Helpdesk')], limit=1, context=context)
        data = []
        for user in res_users_obj.browse(cr, SUPERUSER_ID, users, context=context):
            type_records = []
            res = {'name': user.name, 'type_records': type_records, 'heading_id': user.id, 'panel_id': user.name.replace (" ", "-"), 'heading_href': '#' + user.name.replace (" ", "-")}
            if project_project_ids:
                project_project_records = project_project_obj.browse(cr, SUPERUSER_ID, project_project_ids, context=context)
                for task in project_project_records.type_ids:
                    type_records.append((task.name, len(project_issue_obj.search(cr, SUPERUSER_ID, [('stage_id', '=', task.id), ('user_id', '=', user.id),('project_id', '=', project_project_ids[0])], context=context))))
            data.append(res)
        return request.website._render('web_helpdesk.employee_data', {'datas': data})

    @http.route(['/issue-form-view'], type='json', auth='public', website=True)
    def issue_form_view(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        open_id = pool['project.task.type'].search(cr, SUPERUSER_ID, [('name', '=', 'Open')], limit=1, context=context)
        issue_id = int(kwargs.get('issue_id'))
        project_issue_obj = pool['project.issue']
        project_issue_record = project_issue_obj.browse(cr, SUPERUSER_ID, issue_id, context=context)
        flag = False
        if open_id and project_issue_record.stage_id.name == 'New':
            project_issue_obj.write(cr, SUPERUSER_ID, issue_id, {'stage_id': open_id[0], 'user_id': uid}, context=context)
            flag = True
        html_data = request.website._render('web_helpdesk.issues_form_view', {'issue': project_issue_record})
        return {'html_data': html_data, 'update': flag}

    
    @http.route(['/compose_new_mail'], type='json', auth='public', website=True)
    def compose_new_mail(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        project_issue_obj = pool['project.issue']
        res = {}
        print 'fffffff', kwargs
        if kwargs:
            res.update({'issue': project_issue_obj.browse(cr, SUPERUSER_ID, int(kwargs.get('issue_id')), context=context)})
        return request.website._render('web_helpdesk.compose_new_mail', res)

    @http.route(['/search_issues'], type='json', auth='public', website=True)
    def search_issues(self, **kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        project_issue_obj = pool['project.issue']
        project_project_obj = pool['project.project']
        project_project_ids = project_project_obj.search(cr, SUPERUSER_ID, [('name', '=', 'Helpdesk')], limit=1, context=context)
        domain = [('stage_id', '=', int(kwargs.get('stage_id'))), ('project_id', '=', project_project_ids[0])]
        if str(kwargs.get('stage_name')) == 'New':
            domain.append(('user_id', '=', False))
        else:
            domain.append(('user_id', '=', uid))
        project_issues_ids = project_issue_obj.search(cr, SUPERUSER_ID, domain, context=context)
        project_issues_records = []
        length = len(project_issues_ids)
        if project_issues_ids:
            project_issues_records = project_issue_obj.browse(cr, SUPERUSER_ID, project_issues_ids, context=context)
        html_data = request.website._render('web_helpdesk.issues', {'issues': project_issues_records})
        return {'html_data': html_data, 'record_len': length}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
