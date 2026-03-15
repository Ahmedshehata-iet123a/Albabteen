# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Statement(models.Model):
    _inherit = "account.bank.statement.line"
    account_id = fields.Many2one("account.account")
    code = fields.Char()
    # @api.depends('code')
    # def get_account_id(self):
    #     for rec in self:
    #         rec.account_id=''
    #         account_id = self.env['account.account'].search([('code', '=', rec.code)])
    #         if account_id:
    #             rec.account_id=account_id.id


class Move(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super(Move, self).action_post()
        for record in self:
            for rec in record.line_ids:
                if rec.statement_line_id:
                    if rec.account_id == rec.journal_id.suspense_account_id:
                        if rec.statement_line_id.code:
                            # account_id = self.env['account.account'].search([('code','=',rec.statement_line_id.code)])
                            rec.account_id = rec.statement_line_id.account_id.id
                        else:

                            if rec.statement_line_id.partner_id.customer_rank > 0 and rec.statement_line_id.partner_id.supplier_rank > 0\
                                    and rec.statement_line_id.partner_id:

                                if rec.statement_line_id.amount > 0 and rec.statement_line_id.partner_id:
                                    if rec.statement_line_id.partner_id.property_account_receivable_id:
                                        rec.account_id = rec.statement_line_id.partner_id.property_account_receivable_id.id
                                if rec.statement_line_id.amount < 0 and rec.statement_line_id.partner_id:
                                    if rec.statement_line_id.partner_id.property_account_payable_id:
                                        rec.account_id = rec.statement_line_id.partner_id.property_account_payable_id.id
                            else:
                                if rec.statement_line_id.partner_id.customer_rank > 0 and rec.statement_line_id.partner_id:
                                    if rec.statement_line_id.partner_id.property_account_receivable_id:
                                        rec.account_id = rec.statement_line_id.partner_id.property_account_receivable_id.id
                                if rec.statement_line_id.partner_id.supplier_rank > 0 and rec.statement_line_id.partner_id:
                                    if rec.statement_line_id.partner_id.property_account_payable_id:
                                        rec.account_id = rec.statement_line_id.partner_id.property_account_payable_id.id

        return res

        return res

# class statement_custom_account(models.Model):
#     _name = 'statement_custom_account.statement_custom_account'
#     _description = 'statement_custom_account.statement_custom_account'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
