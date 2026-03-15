from odoo import api, fields, models


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    # sale_id = fields.Many2one(
    #     comodel_name='sale.order',
    #     string='Sale Order',
    #     required=False)



    po_number = fields.Char(
        string='Po Number',tracking=True, translate=True,
        required=False)



    taxed_amount = fields.Float(
        string='Taxable Amount',
        compute='_compute_taxed_amount',
        required=False)

    untaxed_amount = fields.Float(
        string='Untaxable Amount',
        compute='_compute_untaxed_amount',
        required=False)

    disc_amount = fields.Float(
        string='Discount Amount',
        compute='_compute_disc_amount',
        required=False)

    total_before_tax = fields.Float(
        string='Before Discount',
        compute='_compute_total_before_tax',
        required=False)

    @api.depends('invoice_line_ids')
    def _compute_taxed_amount(self):
        for rec in self:
            if rec.invoice_line_ids:
                for line in rec.invoice_line_ids:
                    if line.tax_ids:
                        all_taxes = 0.0000
                        for tax in line.tax_ids:
                            all_taxes += tax.amount

                        rec.taxed_amount += line.price_subtotal
                    else:
                        rec.taxed_amount += 0
            else:
                rec.taxed_amount += 0

    @api.depends('invoice_line_ids')
    def _compute_untaxed_amount(self):
        for rec in self:
            if rec.invoice_line_ids:
                for line in rec.invoice_line_ids:
                    if line.tax_ids:
                        rec.untaxed_amount += 0
                    else:
                        rec.untaxed_amount += line.price_subtotal
            else:
                rec.untaxed_amount += 0

    @api.depends('invoice_line_ids')
    def _compute_disc_amount(self):
        self.disc_amount = 0
        for line in self.invoice_line_ids:
            if line.discount:
                self.disc_amount += ((line.discount/100) * (line.price_unit * line.quantity))
            else:
                self.disc_amount += 0
            if line.discount_fixed:
                self.disc_amount-=line.discount_fixed


    @api.depends('invoice_line_ids')
    def _compute_total_before_tax(self):
        for rec in self:
            rec.total_before_tax = 0
            for line in rec.invoice_line_ids:
                if line:
                    rec.total_before_tax += (line.price_unit * line.quantity)
                else:
                    rec.total_before_tax += 0
        #
        # if self.amount_tax:
        #     self.total_before_tax += self.amount_tax
        # else:
        #     self.total_before_tax += 0

    # @api.model
    # def default_get(self, field):
    #     res = super(AccountMoveInherit, self).default_get(field)
    #     active_model = self.env.context.get('active_model')
    #     if active_model == 'sale.order' and len(self.env.context.get('active_ids', [])) <= 1:
    #         sale_order = self.env[active_model].browse(self.env.context.get('active_id')).exists()
    #         if sale_order:
    #             res.update(
    #                 sale_id=sale_order.id,
    #                 project_id=sale_order.project_id.id
    #             )
    #     return res



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    discount_fixed = fields.Float(
        string="Fixed Discount",
        digits="Discount",
    )
