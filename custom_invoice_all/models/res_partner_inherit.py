from odoo import fields, models, api


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    arabic_name = fields.Char(
        string='Arabic Name',
        required=False)

    arabic_address = fields.Char(
        string='Arabic Address',
        required=False)

    arabic_city = fields.Char(
        string='Arabic City', 
        required=False)
    
    arabic_state = fields.Char(
        string='Arabic State',
        required=False)

    arabic_country = fields.Char(
        string='Arabic Country',
        required=False)

    bank_name = fields.Char(
        string='Bank Name',
        required=False)

    iban = fields.Char(
        string='IBAN',
        required=False)

    arabic_bank_name = fields.Char(
        string='Arabic Bank Name',
        required=False)

    company_registry = fields.Char(
        string='Company CR',
        required=False)

