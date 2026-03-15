from odoo import fields, models, api


class template(models.Model):
    _inherit  = 'product.template'
    is_medical = fields.Boolean()
