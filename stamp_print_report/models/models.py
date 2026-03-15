# -*- coding: utf-8 -*-

from odoo import models, fields, api


class stamp_print_report(models.Model):
    _inherit = "res.company"
    stamp = fields.Binary()

class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"
    stamp = fields.Binary(related='company_id.stamp', readonly=False)