# -*- coding: utf-8 -*-
# from odoo import http


# class StatmentScreen(http.Controller):
#     @http.route('/statment_screen/statment_screen', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/statment_screen/statment_screen/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('statment_screen.listing', {
#             'root': '/statment_screen/statment_screen',
#             'objects': http.request.env['statment_screen.statment_screen'].search([]),
#         })

#     @http.route('/statment_screen/statment_screen/objects/<model("statment_screen.statment_screen"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('statment_screen.object', {
#             'object': obj
#         })
