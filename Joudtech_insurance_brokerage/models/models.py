# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class Move(models.Model):
    _inherit = 'account.move'
    inspol_id = fields.Many2one("insurance.brokerage", string=" Insurance Policy")
    policy_no = fields.Char(related="inspol_id.policy_no", string="POLICY NO", store=True, index=True)
    id_no = fields.Char(related="inspol_id.id_no", string="ID NO", store=True, index=True)
    other_account_id = fields.Many2one("account.account")
    ref = fields.Char(string='Reference', copy=True, tracking=True)

    def action_post(self):
        res = super().action_post()
        for rec in self:
            if rec.other_account_id:
                asset_receivable_line_ids = rec.line_ids.filtered(
                    lambda p: p.account_id.account_type == 'asset_receivable')
                if asset_receivable_line_ids:
                    asset_receivable_line_ids.account_id = rec.other_account_id.id
        return res

    @api.constrains('ref', 'move_type')
    def check_ref(self):
        for rec in self:

            if not rec.ref and rec.move_type == 'entry':
                raise ValidationError(_('Referance must be required'))


class MoveLine(models.Model):
    _inherit = "account.move.line"

    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        for line in self:
            account_type = line.account_id.account_type
            # if line.move_id.is_sale_document(include_receipts=True):
            #     if (line.display_type == 'payment_term') ^ (account_type == 'asset_receivable'):
            #         raise UserError(_("Any journal item on a receivable account must have a due date and vice versa."))
            if line.move_id.is_purchase_document(include_receipts=True):
                if (line.display_type == 'payment_term') ^ (account_type == 'liability_payable'):
                    raise UserError(_("Any journal item on a payable account must have a due date and vice versa."))


class Joudtech_insurance_brokerage(models.Model):
    _name = 'insurance.brokerage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    list_price = fields.Float("PREMIUM", tracking=True, )
    standard_price = fields.Float("Cost Price", compute='get_standard_price', store=True, tracking=True, )
    sponsor_name = fields.Char("SPONSOR NAME", tracking=True, )
    id_no = fields.Char("ID NO", tracking=True, )
    sponsor_no = fields.Char("SPONSOR NO", tracking=True, )
    display_name = fields.Char("Display Name", tracking=True, )
    policy_no = fields.Char("POLICY NO", required=True, tracking=True, )
    id_no = fields.Char("ID NO", tracking=True, )
    user_id = fields.Many2one("res.partner", "USER", required=True, tracking=True, )
    vinv_id = fields.Many2one("account.move", " Purchase invoice/Refund", tracking=True, )
    cinv_id = fields.Many2one("account.move", " Sale invoice/Refund", tracking=True, )
    online_payment_move_id = fields.Many2one("account.move", " Online Payment Move", tracking=True, )
    contract_id = fields.Many2one("account.analytic.account", "Contract id", tracking=True, )
    product_id = fields.Many2one("product.product", "INSU PRODUCT", required=True, tracking=True, )
    state = fields.Selection([('draft', 'draft'), ('done', 'Done'), ('cancel', 'Canceled')] \
                             , string="Status", default='draft', tracking=True, )
    doc_state = fields.Selection([('Accepted', 'Accepted'), ('Rejected', 'Rejected') \
                                     , ('Canceled', 'Canceled')], string="DOC STATUS", required=True, tracking=True, )

    profit_amount = fields.Float("BROKER COMMISSION", tracking=True, )
    date_doc = fields.Date("DOC DATE", required=True, tracking=True, )
    vendor_id = fields.Many2one("res.partner", "Vendor ", tracking=True, )
    date_from = fields.Date("Policy Date", required=True, tracking=True, )
    date_to = fields.Date("Policy To", required=True, tracking=True, )
    # is_online = fields.Boolean("Is Online", required=True, tracking=True, )
    is_online = fields.Selection([('offline', 'offline'), ('online', 'online')], string="Is Online", required=True, tracking=True, )
    _sql_constraints = [
        ('code_policy_uniq', 'unique (policy_no, id_no,date_doc)', 'Policy  already exist !!'),
    ]

    @api.constrains('date_doc')
    def check_date(self):
        if self.date_doc and (self.date_doc > datetime.today().date()):
            raise ValidationError("Date must be less than today")

    @api.constrains('product_id', 'policy_no', 'id_no', 'sponsor_no')
    def check_date_medical(self):
        for rec in self:
            if rec.product_id.is_medical:
                if not rec.policy_no:
                    raise ValidationError("Policy No must be required %s" % (rec.product_id.name))

                if not rec.id_no:
                    raise ValidationError("ID No must be required %s" % (rec.product_id.name))
                if not rec.sponsor_no:
                    raise ValidationError("sponsor  No must be required %s" % (rec.product_id.name))

    @api.depends('list_price', 'profit_amount')
    def get_standard_price(self):
        for rec in self:
            rec.standard_price = rec.list_price - rec.profit_amount

    def set_draft(self):
        for rec in self:
            if rec.state == 'done':

                if rec.cinv_id:
                    rec.cinv_id.button_draft()
                    rec.cinv_id.button_cancel()
                    rec.cinv_id.button_draft()

                if rec.vinv_id:
                    rec.vinv_id.button_draft()
                    rec.vinv_id.button_cancel()
                    rec.vinv_id.button_draft()

                rec.state = 'draft'

    def action_done(self):
        for rec in self:
            name = ''

            name += rec.id_no if rec.id_no else ''
            name += "-" + rec.policy_no if rec.policy_no else ''
            name += "-" + rec.sponsor_name if rec.sponsor_name else ''
            if rec.state == 'draft':
                rec.state = 'done'
                if not rec.cinv_id:
                    rec.cinv_id = rec.create_moves(rec.product_id, rec.user_id, rec.contract_id \
                                                   , rec.list_price, rec.vendor_id, rec.standard_price, \
                                                   rec.id, rec.date_doc if rec.date_doc \
                                                       else datetime.today().date(), name, rec.policy_no)
                else:
                    rec.edit_moves(rec.product_id, rec.user_id, rec.contract_id \
                                   , rec.list_price, rec.vendor_id, rec.standard_price, \
                                   rec.id, rec.date_doc if rec.date_doc \
                                       else datetime.today().date(), name, rec.cinv_id \
                                   , rec.vinv_id)
            if rec.is_online == 'online':
                rec.online_payment_move_id = rec.create_moves(rec.product_id, rec.user_id, rec.contract_id \
                                                              , rec.list_price, rec.vendor_id, rec.standard_price, \
                                                              rec.id, rec.date_doc if rec.date_doc \
                                                                  else datetime.today().date(), name, rec.policy_no,
                                                              is_online='online')

                # if rec.cinv_id:
                #      rec.cinv_id.action_post()
                # if rec.vinv_id:
                #      rec.vinv_id.action_post()

    # @api.model
    # def create(self, vals):
    #     res = super(Joudtech_insurance_brokerage, self).create(vals)
    #     for rec in res:
    #         if rec.state == 'done':
    #             rec.cinv_id, rec.vinv_id = rec.create_moves(rec.product_id, rec.user_id, rec.contract_id \
    #                                                         , rec.list_price, rec.vendor_id, rec.standard_price, rec.id,
    #                                                         rec.date_doc,rec.policy_no if rec.policy_no else rec.sponsor_no)
    #     return res
    def create_data_insurance(self):
        lines = self.env['insurance.brokerage'].sudo().search([('state', '=', 'draft')], limit=1000)

        for rec in lines:
            if rec.cinv_id:
                rec.cinv_id.inspol_id = rec.id
            # if rec.vinv_id:
            #     rec.vinv_id.inspol_id = rec.id
            if rec.cinv_id and rec.vinv_id:
                rec.state = 'done'

    def create_moves(self, product_id, user_id, contract_id \
                     , list_price, vendor_id, standard_price, id, date, policy_no, policy_rec, is_online='offline'):

        move_id = self.env['account.move']
        inv_id = self.env['account.move']
        type = 'out_invoice'
        type_1 = 'in_invoice'
        type = type_1 = 'entry'
        taxes = []
        tax_account_id = ''
        if self.product_id.taxes_id:
            taxes = self.product_id.taxes_id[0]
            tax_account_id = self.env['account.tax.repartition.line'].search(
                [('invoice_tax_id', '=', taxes.id), ('account_id', '!=', False)])
            if tax_account_id:
                tax_account_id = tax_account_id.account_id
        if not is_online == 'online':
            sale_conf_id = self.env['insurrance.conf'].search([('type', '=', 'sale')])
            purchase_conf_id = self.env['insurrance.conf'].search([('type', '=', 'purchase')])
            if taxes and tax_account_id and tax_account_id:
                # tax_amount_before = round(abs(self.list_price)/(1+(taxes.amount/100)),2)
                # tax_amount = round(((taxes.amount/100))*abs(tax_amount_before),2)
                tax_amount = round((abs(self.list_price) * (taxes.amount / 100)), 2)
                inv_id = inv_id.create({

                    'date': date,
                    'journal_id': sale_conf_id.journal_id.id,
                    'ref': policy_rec,
                    'inspol_id': id,
                    'move_type': type,
                    'line_ids': [(0, 0, {
                        'name': policy_no,
                        'debit': abs(list_price) + tax_amount if list_price > 0 else 0,
                        'credit': abs(list_price) + tax_amount if list_price < 0 else 0,
                        'partner_id': user_id.id if user_id else '',

                        'account_id': sale_conf_id.debit_account.id
                    }), (0, 0, {
                        'name': policy_no,
                        'credit': abs(tax_amount) if list_price > 0 else 0,
                        'debit': abs(tax_amount) if list_price < 0 else 0,
                        'account_id': tax_account_id.id,
                    }),
                                 (0, 0, {
                                     'name': policy_no,
                                     'credit': abs(list_price) if list_price > 0 else 0,
                                     'debit': abs(list_price) if list_price < 0 else 0,
                                     'account_id': sale_conf_id.credit_account.id,
                                     'partner_id': vendor_id.id if vendor_id else ''
                                 }),

                                 ]

                })
            else:

                inv_id = inv_id.create({
                    'date': date,
                    'journal_id': sale_conf_id.journal_id.id,
                    'inspol_id': id,
                    'ref': policy_rec,
                    'move_type': type,
                    'line_ids': [(0, 0, {
                        'name': policy_no,
                        'debit': abs(list_price) if list_price > 0 else 0,
                        'credit': abs(list_price) if list_price < 0 else 0,

                        'account_id': sale_conf_id.debit_account.id,
                        'partner_id': user_id.id if user_id else ''
                    }), (0, 0, {
                        'name': policy_no,
                        'credit': abs(list_price) if list_price > 0 else 0,
                        'debit': abs(list_price) if list_price < 0 else 0,
                        'account_id': sale_conf_id.credit_account.id,
                        'partner_id': vendor_id.id if vendor_id else ''
                    })
                                 ]

                })
        else:
            sale_conf_id = self.env['insurrance.conf'].search([('type', '=', 'sale')])
            purchase_conf_id = self.env['insurrance.conf'].search([('type', '=', 'purchase')])
            if taxes and tax_account_id and tax_account_id:
                # tax_amount_before = round(abs(self.list_price)/(1+(taxes.amount/100)),2)
                # tax_amount = round(((taxes.amount/100))*abs(tax_amount_before),2)
                tax_amount = round((abs(self.list_price) * (taxes.amount / 100)), 2)
                inv_id = inv_id.create({

                    'date': date,
                    'journal_id': sale_conf_id.online_journal_id.id,
                    'ref': policy_rec,
                    'inspol_id': id,
                    'move_type': type,
                    'line_ids': [(0, 0, {
                        'name': policy_no,
                        'credit': abs(list_price) + tax_amount if list_price > 0 else 0,
                        'debit': abs(list_price) + tax_amount if list_price < 0 else 0,
                        'partner_id': user_id.id if user_id else '',

                        'account_id': sale_conf_id.debit_account.id
                    }), (0, 0, {
                        'name': policy_no,
                        'debit': abs(tax_amount) if list_price > 0 else 0,
                        'credit': abs(tax_amount) if list_price < 0 else 0,
                        'account_id': tax_account_id.id,
                    }),
                     (0, 0, {
                         'name': policy_no,
                         'debit': abs(list_price) if list_price > 0 else 0,
                         'credit': abs(list_price) if list_price < 0 else 0,
                         'account_id': sale_conf_id.credit_account.id,
                         'partner_id': vendor_id.id if vendor_id else ''
                     }),
                                 ]

                })
            else:

                inv_id = inv_id.create({
                    'date': date,
                    'journal_id': sale_conf_id.online_journal_id.id,
                    'inspol_id': id,
                    'ref': policy_rec,
                    'move_type': type,
                    'line_ids': [(0, 0, {
                        'name': policy_no,
                        'credit': abs(list_price) if list_price > 0 else 0,
                        'debit': abs(list_price) if list_price < 0 else 0,

                        'account_id': sale_conf_id.debit_account.id,
                        'partner_id': user_id.id if user_id else ''
                    }), (0, 0, {
                        'name': policy_no,
                        'debit': abs(list_price) if list_price > 0 else 0,
                        'credit': abs(list_price) if list_price < 0 else 0,
                        'account_id': sale_conf_id.credit_account.id,
                        'partner_id': vendor_id.id if vendor_id else ''
                    })
                                 ]

                })
        # taxes = []
        # taxes = []
        # tax_account_id = ''
        # if self.product_id.supplier_taxes_id:
        #     taxes = self.product_id.supplier_taxes_id[0]
        #     tax_account_id = self.env['account.tax.repartition.line'].search(
        #         [('invoice_tax_id', '=', taxes.id), ('account_id', '!=', False)])
        #     if tax_account_id:
        #         tax_account_id = tax_account_id.account_id
        #
        # if taxes and tax_account_id and tax_account_id:
        #     # tax_amount_before = round(abs(self.list_price)/(1 + (taxes.amount / 100)) , 2)
        #     #
        #     #
        #     # tax_amount = round(( (taxes.amount / 100)) * abs(tax_amount_before), 2)
        #     tax_amount = round((abs(self.standard_price) * (taxes.amount / 100)), 2)
        #     move_id = move_id.create({
        #         'partner_id': vendor_id.id,
        #         'date': date,
        #         'inspol_id': id,
        #         'move_type': type_1,
        #         'journal_id': purchase_conf_id.journal_id.id,
        #
        #         'line_ids': [(0, 0, {
        #             'name': policy_no,
        #             'credit': abs(standard_price) if standard_price > 0 else 0,
        #             'debit': abs(standard_price) if standard_price < 0 else 0,
        #
        #             'account_id': purchase_conf_id.debit_account.id
        #         }),
        #                      (0, 0, {
        #                          'name': policy_no,
        #                          'credit': abs(tax_amount) if standard_price < 0 else 0,
        #                          'debit': abs(tax_amount) if standard_price > 0 else 0,
        #
        #                          'account_id': tax_account_id.id
        #                      }),
        #
        #                      (0, 0, {
        #                          'name': policy_no,
        #                          'debit': abs(standard_price) + tax_amount if standard_price < 0 else 0,
        #                          'credit': abs(standard_price) + tax_amount if standard_price > 0 else 0,
        #                          'account_id': purchase_conf_id.credit_account.id
        #                      })
        #                      ]
        #
        #     })
        # else:
        #     move_id = move_id.create({
        #         'partner_id': vendor_id.id,
        #         'date': date,
        #         'inspol_id': id,
        #         'move_type': type_1,
        #         'journal_id': purchase_conf_id.journal_id.id,
        #
        #         'line_ids': [(0, 0, {
        #             'name': policy_no,
        #             'credit': abs(standard_price) if standard_price < 0 else 0,
        #             'debit': abs(standard_price) if standard_price > 0 else 0,
        #
        #             'account_id': purchase_conf_id.debit_account.id
        #         }), (0, 0, {
        #             'name': policy_no,
        #             'debit': abs(standard_price) if standard_price < 0 else 0,
        #             'credit': abs(standard_price) if standard_price > 0 else 0,
        #             'account_id': purchase_conf_id.credit_account.id
        #         })
        #                      ]
        #
        #     })

        inv_id.action_post()
        # move_id.action_post()

        for rec in inv_id.invoice_line_ids:
            rec.name = policy_no
        # for rec in move_id.invoice_line_ids:
        #     rec.name = policy_no

        return inv_id

    def edit_moves(self, product_id, user_id, contract_id \
                   , list_price, vendor_id, standard_price, id, date, policy_no, inv_id, move_id):

        if inv_id and move_id:
            self.env.cr.execute('delete from account_move_line where move_id in (%s,%s)' % (inv_id.id, move_id.id))
        else:
            self.env.cr.execute('delete from account_move_line where move_id in (%s)' % (inv_id.id))

        taxes = []
        tax_account_id = ''
        if self.product_id.taxes_id:
            taxes = self.product_id.taxes_id[0]
            tax_account_id = self.env['account.tax.repartition.line'].search(
                [('invoice_tax_id', '=', taxes.id), ('account_id', '!=', False)])
            if tax_account_id:
                tax_account_id = tax_account_id.account_id

        sale_conf_id = self.env['insurrance.conf'].search([('type', '=', 'sale')])
        purchase_conf_id = self.env['insurrance.conf'].search([('type', '=', 'purchase')])
        if taxes and tax_account_id and tax_account_id:
            # tax_amount_before = round(abs(self.list_price)/(1+(taxes.amount/100)),2)
            # tax_amount = round(((taxes.amount/100))*abs(tax_amount_before),2)
            tax_amount = round((abs(self.list_price) * (taxes.amount / 100)), 2)
            inv_id.line_ids = [(0, 0, {
                'name': policy_no,
                'debit': abs(list_price) + tax_amount if list_price > 0 else 0,
                'credit': abs(list_price) + tax_amount if list_price < 0 else 0,

                'account_id': sale_conf_id.debit_account.id,
                'partner_id': user_id.id if user_id else ''
            }), (0, 0, {
                'name': policy_no,
                'credit': abs(tax_amount) if list_price > 0 else 0,
                'debit': abs(tax_amount) if list_price < 0 else 0,
                'account_id': tax_account_id.id,
            }),
                               (0, 0, {
                                   'name': policy_no,
                                   'credit': abs(list_price) if list_price > 0 else 0,
                                   'debit': abs(list_price) if list_price < 0 else 0,
                                   'account_id': sale_conf_id.credit_account.id,
                                   'partner_id': vendor_id.id if vendor_id else ''

                               }),

                               ]


        else:

            inv_id.line_ids = [(0, 0, {
                'name': policy_no,
                'debit': abs(list_price) if list_price > 0 else 0,
                'credit': abs(list_price) if list_price < 0 else 0,

                'account_id': sale_conf_id.debit_account.id,
                'partner_id': user_id.id if user_id else ''
            }), (0, 0, {
                'name': policy_no,
                'credit': abs(list_price) if list_price > 0 else 0,
                'debit': abs(list_price) if list_price < 0 else 0,
                'account_id': sale_conf_id.credit_account.id,
                'partner_id': vendor_id.id if vendor_id else ''
            })
                               ]

        # taxes = []
        # taxes = []
        # tax_account_id = ''
        # if self.product_id.supplier_taxes_id:
        #     taxes = self.product_id.supplier_taxes_id[0]
        #     tax_account_id = self.env['account.tax.repartition.line'].search(
        #         [('invoice_tax_id', '=', taxes.id), ('account_id', '!=', False)])
        #     if tax_account_id:
        #         tax_account_id = tax_account_id.account_id
        #
        # if taxes and tax_account_id and tax_account_id:
        #     # tax_amount_before = round(abs(self.list_price)/(1 + (taxes.amount / 100)) , 2)
        #     #
        #     #
        #     # tax_amount = round(( (taxes.amount / 100)) * abs(tax_amount_before), 2)
        #     tax_amount = round((abs(self.standard_price) * (taxes.amount / 100)), 2)
        #     move_id.line_ids =[(0, 0, {
        #             'name': policy_no,
        #             'credit': abs(standard_price) if standard_price < 0 else 0,
        #             'debit': abs(standard_price) if standard_price > 0 else 0,
        #
        #
        #             'account_id': purchase_conf_id.debit_account.id
        #         }),
        #                      (0, 0, {
        #                          'name': policy_no,
        #                          'credit': abs(tax_amount) if standard_price < 0 else 0,
        #                          'debit': abs(tax_amount) if standard_price > 0 else 0,
        #
        #                          'account_id': tax_account_id.id
        #                      }),
        #
        #                      (0, 0, {
        #                          'name': policy_no,
        #                          'debit': abs(standard_price) + tax_amount if standard_price < 0 else 0,
        #                          'credit': abs(standard_price) + tax_amount if standard_price > 0 else 0,
        #                          'account_id': purchase_conf_id.credit_account.id
        #                      })
        #                      ]
        #
        #
        # else:
        #     move_id.line_ids= [(0, 0, {
        #             'name': policy_no,
        #             'credit': abs(standard_price) if standard_price < 0 else 0,
        #             'debit': abs(standard_price) if standard_price > 0 else 0,
        #
        #             'account_id': purchase_conf_id.debit_account.id
        #         }), (0, 0, {
        #             'name': policy_no,
        #             'debit': abs(standard_price) if list_price < 0 else 0,
        #             'credit': abs(standard_price) if standard_price > 0 else 0,
        #             'account_id': purchase_conf_id.credit_account.id
        #         })
        #                      ]

        inv_id.action_post()
        # move_id.action_post()

        for rec in inv_id.invoice_line_ids:
            rec.name = policy_no
        # for rec in move_id.invoice_line_ids:
        #     rec.name = policy_no

        return inv_id

    def action_view_moves(self):
        return {
            'name': ('Moves'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'account.move',
            'context': {'default_inspol_id': self.id},
            'type': 'ir.actions.act_window',
            'domain': [('inspol_id', '=', self.id)],
            'target': 'current',
        }

    def unlink(self):
        for rec in self:
            move_ids = self.env['account.move'].search([('inspol_id', '=', rec.id)])
            if rec.state == 'done' or move_ids:
                raise ValidationError("You Can't delete policy done")
        res = super(Joudtech_insurance_brokerage, self).unlink()

        return res


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_get_suggested_recipients(self):
        """ Returns suggested recipients for ids. Those are a list of
        tuple (partner_id, partner_name, reason), to be managed by Chatter. """
        result = dict((res_id, []) for res_id in self.ids)
        if 'user_id' in self._fields:
            for obj in self.sudo():  # SUPERUSER because of a read on res.users that would crash otherwise

                if self._name != 'insurance.brokerage':
                    if not obj.user_id or not obj.user_id.partner_id:
                        continue
                    obj._message_add_suggested_recipient(result, partner=obj.user_id.partner_id,
                                                         reason=self._fields['user_id'].string)
        return result
