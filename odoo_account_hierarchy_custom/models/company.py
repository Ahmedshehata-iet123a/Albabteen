from odoo import fields, models, api


class Company(models.Model):
    _inherit = "res.company"
    prefix_char = fields.Char()
    sequence = fields.Integer(default=3)
