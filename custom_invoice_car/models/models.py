# -*- coding: utf-8 -*-

from odoo import models, fields, api


class custom_invoice_car(models.Model):
    _inherit = "account.move"
    car_model = fields.Char()
    car_number = fields.Char()