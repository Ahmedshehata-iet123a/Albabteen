# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerLedgerLoading(http.Controller):
#     @http.route('/partner_ledger_loading/partner_ledger_loading', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_ledger_loading/partner_ledger_loading/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_ledger_loading.listing', {
#             'root': '/partner_ledger_loading/partner_ledger_loading',
#             'objects': http.request.env['partner_ledger_loading.partner_ledger_loading'].search([]),
#         })

#     @http.route('/partner_ledger_loading/partner_ledger_loading/objects/<model("partner_ledger_loading.partner_ledger_loading"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_ledger_loading.object', {
#             'object': obj
#         })
