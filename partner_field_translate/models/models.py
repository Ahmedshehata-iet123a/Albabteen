# -*- coding: utf-8 -*-

from odoo import models, fields, api


class partner_field_translate(models.Model):
    _inherit = "res.partner"
    city = fields.Char(string="city", translate=True)
    street = fields.Char(string="street", translate=True)
    # name = fields.Char(string="Name", translate=True)
    bank_name = fields.Char(
        string='Bank Name',
        translate=True,
        required=False)
class Country(models.Model):
    _inherit = "res.country"
    name = fields.Char(string="city", translate=True)

class State(models.Model):
    _inherit = "res.country.state"
    name = fields.Char(string="State Name", translate=True)