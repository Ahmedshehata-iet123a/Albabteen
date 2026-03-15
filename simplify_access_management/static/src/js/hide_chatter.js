/** @odoo-module **/

import { FormRenderer } from "@web/views/form/form_renderer";
import { ListController } from "@web/views/list/list_controller";
import { FormController } from "@web/views/form/form_controller";
import { session } from "@web/session";
const { patch } = require('web.utils');
var rpc = require('web.rpc');

patch(FormRenderer.prototype, 'simplify_access_management/static/src/js/hide_chatter.js', {
    setup() {
        const self = this;
        this._super();

        return Promise.resolve(this._super()).then(function (ev) {
            var hash = window.location.hash.substring(1);
            hash = JSON.parse('{"' + hash.replace(/&/g, '","').replace(/=/g,'":"') + '"}', function(key, value) { return key===""?value:decodeURIComponent(value) })
            if (hash.cids != null && hash.model != null){
                rpc.query({
                    model:'access.management',
                    method: 'get_chatter_hide_details',
                    args: [session.user_id, parseInt(hash.cids.charAt(0)), hash.model]
                }).then(function(result){
                    if(result['hide_send_mail'] == false)
                    {
                        var btn1 = setInterval(function() {
                        if ($('.o_ChatterTopbar_buttonSendMessage').length) {
                                $('.o_ChatterTopbar_buttonSendMessage').remove();
                                clearInterval(btn1);
                        }
                        }, 50);
                    }
                    if(result['hide_log_notes'] == false)
                    {
                        var btn2 = setInterval(function() {
                        if ($('.o_ChatterTopbar_buttonLogNote').length) {
                                $('.o_ChatterTopbar_buttonLogNote').remove();
                                clearInterval(btn2);
                        }
                        }, 50);
                    }
                    if(result['hide_schedule_activity'] == false)
                    {
                        var btn3 = setInterval(function() {
                        if ($('.o_ChatterTopbar_buttonScheduleActivity').length) {
                                $('.o_ChatterTopbar_buttonScheduleActivity').remove();
                                clearInterval(btn3);
                        }
                        }, 50);
                    }

                });
            }
        });
    },
});