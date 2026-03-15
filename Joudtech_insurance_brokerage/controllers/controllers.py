# -*- coding: utf-8 -*-
# from odoo import http


# class DvitInsuranceBrokerage(http.Controller):
#     @http.route('/Joudtech_insurance_brokerage/Joudtech_insurance_brokerage/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/Joudtech_insurance_brokerage/Joudtech_insurance_brokerage/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('Joudtech_insurance_brokerage.listing', {
#             'root': '/Joudtech_insurance_brokerage/Joudtech_insurance_brokerage',
#             'objects': http.request.env['Joudtech_insurance_brokerage.Joudtech_insurance_brokerage'].search([]),
#         })

#     @http.route('/Joudtech_insurance_brokerage/Joudtech_insurance_brokerage/objects/<model("Joudtech_insurance_brokerage.Joudtech_insurance_brokerage"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('Joudtech_insurance_brokerage.object', {
#             'object': obj
#         })
