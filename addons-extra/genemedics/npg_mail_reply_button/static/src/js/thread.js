odoo.define('npg_mail_reply_button.ChatThread', function (require) {
"use strict";

var ChatThread = require('mail.ChatThread');
var ChatterComposer = require('mail.ChatComposer');
var config = require('web.config');

var chat_manager = require('mail.chat_manager');

var ajax = require('web.ajax');
var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var form_common = require('web.form_common');
var session = require('web.session');
var web_client = require('web.web_client');

var _t = core._t;
var qweb = core.qweb;

ChatThread.include({

    on_click_o_thread_message_reply: function(event) {
        var self = this;
        this.open_composer();
       // var message_id = $(event.currentTarget).data('message-id');
       // this.trigger("open_composer", message_id);
    },
    
    init: function(parent, dataset, options) {
        this._super(parent);
        this.thread_dataset = dataset;
        if (this.followers) {
            this.$('.o_chatter_topbar').append(this.followers.$el);
        }
   		 this.events = _.extend(this.events, {
            "click .o_thread_message_reply": "on_click_o_thread_message_reply",
        });
    },
    
    open_composer: function (options) {
        var self = this;
        var old_composer = this.composer;
        // create the new composer
        this.composer = new ChatterComposer(this, this.thread_dataset, {
            context: this.context,
            input_min_height: 50,
            input_max_height: Number.MAX_VALUE, // no max_height limit for the chatter
            input_baseline: 14,
            internal_subtypes: this.options.internal_subtypes,
            is_log: options && options.is_log,
            record_name: this.record_name,
            get_channel_info: function () {
                return { res_id: self.res_id, res_model: self.model };
            },
        });
        this.composer.insertAfter(this.$('.o_mail_thread')).then(function () {
            // destroy existing composer
            if (old_composer) {
                old_composer.destroy();
            }
            if (!config.device.touch) {
                self.composer.focus();
            }
            self.composer.on('post_message', self, self.on_post_message);
            self.composer.on('need_refresh', self, self.refresh_followers);
        });
        
       },
       
     refresh_followers: function () {
        if (this.followers) {
            this.followers.read_value();
        }
    },
        
    on_post_message: function (message) {
        var self = this;
        chat_manager
            .post_message_in_document(this.model, this.res_id, message)
            .then(function () {
                self.close_composer();
                if (message.partner_ids.length) {
                    self.refresh_followers(); // refresh followers' list
                }
            })
            .fail(function () {
                // todo: display notification
            });
    },

    
});

});