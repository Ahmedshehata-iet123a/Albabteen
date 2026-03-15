from odoo import fields, models, api


class Level(models.Model):
    _name = 'account.level'
    _description = 'Account Level'

    name = fields.Integer()
    prefix = fields.Integer()
    is_show = fields.Boolean()
