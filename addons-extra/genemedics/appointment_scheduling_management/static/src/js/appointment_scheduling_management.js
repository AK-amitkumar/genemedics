odoo.define('appointment_scheduling_management', function (require) {
'use strict';

var WebClient = require('web.WebClient');
var core = require('web.core');
var Model = require('web.DataModel');

var QWeb = core.qweb;

WebClient.include({
    show_application: function() {
        return $.when(this._super.apply(this, arguments)).then(function(){
        	var Users = new Model('res.users');
        	Users.call('has_group', ['appointment_scheduling_management.lead_user']).done(function(lead_user) {
        		if(lead_user){
        			$('#oe_main_menu_navbar').hide()
        			$('.oe_leftbar').remove()
        		}
        	});
        });
    }
});

});