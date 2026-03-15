# -*- coding: utf-8 -*-
# from odoo import http


# class DataMigrationModule(http.Controller):
#     @http.route('/data_migration_module/data_migration_module', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/data_migration_module/data_migration_module/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('data_migration_module.listing', {
#             'root': '/data_migration_module/data_migration_module',
#             'objects': http.request.env['data_migration_module.data_migration_module'].search([]),
#         })

#     @http.route('/data_migration_module/data_migration_module/objects/<model("data_migration_module.data_migration_module"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('data_migration_module.object', {
#             'object': obj
#         })
