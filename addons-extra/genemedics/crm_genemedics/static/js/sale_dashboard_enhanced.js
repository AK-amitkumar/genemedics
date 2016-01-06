odoo.define('crm_genemedics.sale_dashboard_enhanced', function (require) {
"use strict";

var SalesTeamDashboardView = require('sales_team.dashboard');
var Model = require('web.Model');
var core = require('web.core');
var formats = require('web.formats');
var Model = require('web.Model');
var session = require('web.session');
var KanbanView = require('web_kanban.KanbanView');

var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;


SalesTeamDashboardView.include({

    on_dashboard_action_clicked: function(ev){
        ev.preventDefault();

        var self = this;
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        var action_extra = $action.data('extra');
        var additional_context = {}

        // TODO: find a better way to add defaults to search view
        if (action_name === 'calendar.action_calendar_event') {
            additional_context['search_default_mymeetings'] = 1;
        } else if (action_name === 'crm.crm_lead_action_activities') {
            if (action_extra === 'today') {
                additional_context['search_default_today'] = 1;
            } else if (action_extra === 'this_week') {
                additional_context['search_default_this_week'] = 1;
            } else if (action_extra === 'overdue') {
                additional_context['search_default_overdue'] = 1;
            }
        } else if (action_name === 'crm.crm_opportunity_report_action_graph') {
            additional_context['search_default_won'] = 1;
        }else if (action_name === 'crm.crm_lead_action_all_activities') {
            if (action_extra === 'today') {
                additional_context['search_default_today'] = 1;
            } else if (action_extra === 'this_week') {
                additional_context['search_default_this_week'] = 1;
            } else if (action_extra === 'overdue') {
                additional_context['search_default_overdue'] = 1;
            }
        }
        
        new Model("ir.model.data")
            .call("xmlid_to_res_id", [action_name])
            .then(function(data) {
                if (data){
                   self.do_action(data, {additional_context: additional_context});
                }
            });
	}
});

});
