/** @odoo-module **/

import { FormRenderer } from "@web/views/form/form_renderer";
import { ListController } from "@web/views/list/list_controller";
import { FormController } from "@web/views/form/form_controller";
import { ListRenderer } from "@web/views/list/list_renderer";
import { session } from "@web/session";
const { patch } = require('web.utils');
const { onMounted, onPatched, useRef } = owl;
var rpc = require('web.rpc');

patch(ListRenderer.prototype, 'simplify_access_management/static/src/js/hide_export.js', {

    setup() {
        const self = this;
        this._super();

        return Promise.resolve(this._super()).then(function (ev) {
            var hash = window.location.hash.substring(1);
            hash = JSON.parse('{"' + hash.replace(/&/g, '","').replace(/=/g,'":"') + '"}', function(key, value) { return key===""?value:decodeURIComponent(value) })
            if (hash.cids != null && hash.model != null){
                rpc.query({
                    model:'access.management',
                    method: 'is_export_hide',
                    args: [session.user_id, parseInt(hash.cids.charAt(0)), hash.model]
                }).then(function(result){
                    if(result) {
                        var btn1 = setInterval(function() {
                        if ($('.o_list_export_xlsx').length) {
                                $('.o_list_export_xlsx').remove();
                                clearInterval(btn1);
                        }
                        }, 50);
                    }
                });
            }

        });
    }

});
