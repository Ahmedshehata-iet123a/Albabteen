# -*- coding: utf-8 -*-
# from odoo import http


# class StatementCustomAccount(http.Controller):
#     @http.route('/statement_custom_account/statement_custom_account', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/statement_custom_account/statement_custom_account/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('statement_custom_account.listing', {
#             'root': '/statement_custom_account/statement_custom_account',
#             'objects': http.request.env['statement_custom_account.statement_custom_account'].search([]),
#         })

#     @http.route('/statement_custom_account/statement_custom_account/objects/<model("statement_custom_account.statement_custom_account"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('statement_custom_account.object', {
#             'object': obj
#         })
