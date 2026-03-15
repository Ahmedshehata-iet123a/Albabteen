# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime

from odoo.exceptions import ValidationError,UserError

class CustomBankStatment(models.Model):
    _name = "custom.bank.statment"

    name = fields.Char('Reference')
    date = fields.Date('Date',default=fields.Date.today())
    currency_id = fields.Many2one('res.currency',default= lambda self: self.env.user.company_id.currency_id.id)
    journal_id = fields.Many2one('account.journal', domain="[('type', 'in', ['cash', 'bank'])]")
    line_ids = fields.One2many('custom.bank.statment.line','custom_statment_id')
    state = fields.Selection([('draft', 'Draft'),
                             ('confirm', 'Confirmed')],
                             default='draft')
    stat_id = fields.Many2one('account.bank.statement')


    def get_journals(self):
        print('---->', self.stat_id)
        if self.stat_id:
            print('---->', self.stat_id)
            ids = self.stat_id.line_ids.ids
            return {
                'type': 'ir.actions.act_window',
                'name': 'Journal Enteries',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'context': {},
                'domain': [('statement_line_id', 'in', ids)],
            }

    def action_confirm(self):
        vals_list=[]
        print('--->',self.journal_id.name,self.journal_id.suspense_account_id)
        for i in self.line_ids:
                account = False
                account_rec = self.env['account.account'].search([('code', '=', i.code)])
                if account_rec:
                    account = account_rec[0].id
                print('--->code', i.account_id.code, i.account_id)
                values = {
                    'date': i.date,
                    'payment_ref': i.payment_ref,
                    'ref': i.ref,
                    'partner_id': i.partner_id.id,
                    'amount': i.amount,
                    'currency_id': i.currency_id.id,
                    'journal_id': self.journal_id.id,
                    'code': i.account_id.code if i.account_id else False,
                    'account_id': i.account_id.id if i.account_id else False,
                    'partner_name': i.partner_name
                }
                vals_list.append((0, 0, values))
        statement_vals = {
            'name': 'Statement Of ' + str(datetime.today().date()),
            'journal_id': self.journal_id.id,
            'date':self.date,
            'line_ids': vals_list
            }
        if len(vals_list) != 0:
            statement = self.create_statement(statement_vals)
        self.state = 'confirm'
        # self.stat_id = statement.id
        self.name = 'Statement Of ' + str(datetime.today().date())

    def create_statement(self, values):
        statement = self.env['account.bank.statement'].create(values)
        self.stat_id = statement.id
        print('--->', statement)
        return statement

class CustomBankStatmentLine(models.Model):
    _name = "custom.bank.statment.line"

    custom_statment_id = fields.Many2one('custom.bank.statment')
    partner_id = fields.Many2one('res.partner')
    account_id = fields.Many2one('account.account')
    payment_ref = fields.Char('Reference')
    partner_name = fields.Char('Partner Name')
    ref = fields.Char('label')
    code = fields.Char('code')
    date = fields.Date('Date',default=fields.Date.today())
    currency_id = fields.Many2one('res.currency',related='custom_statment_id.currency_id')
    amount = fields.Monetary(currency_field="currency_id",)

    @api.constrains('account_id','partner_id')
    def _check_constrain_code(self):
        for rec in self:
           if not rec.partner_id:
               if not rec.account_id:
                   print(">>>>>>>>>>>>>>>>.",rec.ref)
                   raise ValidationError(_("You must add code %s"%(rec.ref)))



    @api.onchange('code')
    def get_account_by_code(self):
        for i in self:
            account = self.env['account.account'].search([('code','=',i.code)])
            if account:
                i.account_id = account[0].id



    # @api.constrains('account_id')
    # def check_on_account_id:
    #     for i in self:
    #         if not i.account_id:

class Statement(models.Model):
    _inherit="account.bank.statement"

    @api.depends('line_ids.internal_index', 'line_ids.state')
    def _compute_date_index(self):
        for stmt in self:
            print(';;;;;;;;', stmt.date)
            sorted_lines = stmt.line_ids.sorted('internal_index')
            stmt.first_line_index = sorted_lines[:1].internal_index
            if not stmt.date:
                stmt.date = sorted_lines.filtered(lambda l: l.state == 'posted')[-1:].date
