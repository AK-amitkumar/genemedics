odoo.define('crm_helpdesk_features.chat_manager', function (require) {
"use strict";

var Chat_manager = require('mail.chat_manager');
var Systray = require('mail.systray');
var bus = require('bus.bus').bus;
var core = require('web.core');
var data = require('web.data');
var Model = require('web.Model');
var session = require('web.session');
var time = require('web.time');
var web_client = require('web.web_client');



function update_channel_unread_counter (channel, counter) {
// modifified below channel.is_chat to !channel.mass_mailing to show all channels not set to mail to in count
	if (!channel.mass_mailing) {
	        chat_unread_counter = chat_unread_counter - channel.unread_counter + counter;
	  }
	  channel.unread_counter = counter;
	    chat_manager.bus.trigger("update_channel_unread_counter", channel);
	}


//modified below add beep() in if (bus.is_odoo_focused())
function notify_incoming_message (msg, options) {
    var title = _t('New message');
    if (msg.author_id[1]) {
        title = _.escape(msg.author_id[1]);
    }
    var content = parse_and_transform(msg.body, strip_html).substr(0, preview_msg_max_size);

    if (bus.is_odoo_focused()) {
        if (!options.is_displayed) {
            web_client.do_notify(title, content);
            beep();
        }
    } else {
        global_unread_counter++;
        var tab_title = _.str.sprintf(_t("%d Messages"), global_unread_counter);
        web_client.set_title_part("_chat", tab_title);

        if (Notification && Notification.permission === "granted") {
            if (bus.is_master) {
                new Notification(title, {body: content, icon: "/mail/static/src/img/odoo_o.png", silent: false});
            }
        } else {
            web_client.do_notify(title, content);
            if (bus.is_master) {
                beep();
            }
        }
    }
}

// This function calls the above modified Functions
function add_message(data, options) {
    options = options || {};
    var msg = _.findWhere(messages, { id: data.id });

    if (!msg) {
        msg = make_message(data);
        // Keep the array ordered by date when inserting the new message
        messages.splice(_.sortedIndex(messages, msg, 'id'), 0, msg);
        _.each(msg.channel_ids, function (channel_id) {
            var channel = chat_manager.get_channel(channel_id);
            if (channel) {
                add_to_cache(msg, []);
                if (options.domain && options.domain !== []) {
                    add_to_cache(msg, options.domain);
                }
                if (channel.hidden) {
                    channel.hidden = false;
                    chat_manager.bus.trigger('new_channel', channel);
                }
                if (!msg.author_id || msg.author_id[0] !== session.partner_id) {
                    if (options.increment_unread) {
                        update_channel_unread_counter(channel, channel.unread_counter+1);
                    }
                    if (options.show_notification) {
                        var query = {is_displayed: false};
                        chat_manager.bus.trigger('anyone_listening', channel, query);
                        notify_incoming_message(msg, query);
                    }
                }
            }
        });
        if (!options.silent) {
            chat_manager.bus.trigger('new_message', msg);
        }
    } else if (options.domain && options.domain !== []) {
        add_to_cache(msg, options.domain);
    }
    return msg;
}

// Attempt to Override below to call above modifications to notify_incoming_message and update_channel_unread_counter

Chat_manager.include({
	
    get_chat_unread_counter: function () {
        return chat_unread_counter;
    },

    get_messages: function (options) {
        var channel;

        if ('channel_id' in options && options.load_more) {
            // get channel messages, force load_more
            channel = this.get_channel(options.channel_id);
            return fetch_from_channel(channel, {domain: options.domain || {}, load_more: true});
        }
        if ('channel_id' in options) {
            // channel message, check in cache first
            channel = this.get_channel(options.channel_id);
            var channel_cache = get_channel_cache(channel, options.domain);
            if (channel_cache.loaded) {
                return $.when(channel_cache.messages);
            } else {
                return fetch_from_channel(channel, {domain: options.domain});
            }
        }
        if ('ids' in options) {
            // get messages from their ids (chatter is the main use case)
            return fetch_document_messages(options.ids, options).then(function(result) {
                chat_manager.mark_as_read(options.ids);
                return result;
            });
        }
        if ('model' in options && 'res_id' in options) {
            // get messages for a chatter, when it doesn't know the ids (use
            // case is when using the full composer)
            var domain = [['model', '=', options.model], ['res_id', '=', options.res_id]];
            MessageModel.call('message_fetch', [domain], {limit: 30}).then(function (msgs) {
                return _.map(msgs, add_message);
            });
        }
    },
    
    get_channels_preview: function (channels) {
        var channels_preview = _.map(channels, function (channel) {
            var info = _.pick(channel, 'id', 'is_chat', 'name', 'status', 'unread_counter');
            info.last_message = _.last(channel.cache['[]'].messages);
            if (!info.is_chat) {
                info.image_src = '/web/image/mail.channel/'+channel.id+'/image_small';
            } else if (channel.direct_partner_id) {
                info.image_src = '/web/image/res.partner/'+channel.direct_partner_id+'/image_small';
            } else {
                info.image_src = '/mail/static/src/img/smiley/avatar.jpg';
            }
            return info;
        });
        if (!channels_preview_def) {
            var missing_channel_ids = _.pluck(_.where(channels_preview, {last_message: undefined}), 'id');
            if (missing_channel_ids.length) {
                channels_preview_def = ChannelModel
                    .call('channel_fetch_preview', [missing_channel_ids], {}, {shadow: true})
                    .then(function (channels) {
                        _.each(channels, function (channel) {
                            var msg = add_message(channel.last_message);
                            _.findWhere(channels_preview, {id: channel.id}).last_message = msg;
                        });
                    });
            } else {
                channels_preview_def = $.when();
            }
        }
        return channels_preview_def.then(function () {
            return _.filter(channels_preview, function (channel) {
                return channel.last_message;  // remove empty channels
            });
        });
    },

});
});
