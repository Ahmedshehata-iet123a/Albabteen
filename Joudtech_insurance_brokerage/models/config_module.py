
from datetime import datetime

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Move(models.Model):
    _name = 'insurrance.conf'
    type = fields.Selection([('sale','sale'),('purchase','purchase')])
    debit_account = fields.Many2one("account.account")
    credit_account = fields.Many2one("account.account")
    journal_id = fields.Many2one("account.journal")
    online_journal_id = fields.Many2one("account.journal",tracking=True)
