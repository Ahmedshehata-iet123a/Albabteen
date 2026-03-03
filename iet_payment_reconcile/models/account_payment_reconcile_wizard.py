import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountPaymentReconcileWizard(models.TransientModel):
    _name = 'account.payment.reconcile.wizard'
    _description = 'Auto FIFO Payment-Invoice/Bill Reconciliation Wizard'

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        domain="[('id', 'in', available_partner_ids)]",
        help="Leave empty to process ALL partners of the selected type.",
    )
    available_partner_ids = fields.Many2many(
        'res.partner',
        compute='_compute_available_partner_ids',
    )
    reconcile_type = fields.Selection([
        ('customer', 'Customers (Invoices)'),
        ('vendor', 'Vendors (Bills)'),
        ('both', 'Both'),
    ], string='Type', default='customer', required=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
    )

    @api.depends('reconcile_type', 'company_id')
    def _compute_available_partner_ids(self):
        for rec in self:
            ids = set()
            if rec.reconcile_type in ('customer', 'both'):
                ids.update(rec._get_all_customer_ids())
            if rec.reconcile_type in ('vendor', 'both'):
                ids.update(rec._get_all_vendor_ids())
            rec.available_partner_ids = list(ids)

    def _get_all_customer_ids(self):
        """Partners with open receivable lines on posted out_invoices
        OR any other unreconciled credit on receivable account.
        """
        self.env.cr.execute("""
            SELECT DISTINCT aml.partner_id
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN account_move am ON am.id = aml.move_id
            WHERE aml.company_id = %s
              AND aa.account_type = 'asset_receivable'
              AND aml.reconciled = FALSE
              AND aml.partner_id IS NOT NULL
              AND am.state = 'posted'
              AND (
                  (aml.amount_residual > 0 AND am.move_type = 'out_invoice') -- Open Invoices
                  OR 
                  (aml.amount_residual < 0) -- Any available credit (Payment or Journal Entry)
              )
        """, [self.company_id.id])
        return [r[0] for r in self.env.cr.fetchall()]

    def _get_all_vendor_ids(self):
        """Partners with open payable lines on posted in_invoices
        OR any other unreconciled debit on payable account.
        """
        self.env.cr.execute("""
            SELECT DISTINCT aml.partner_id
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN account_move am ON am.id = aml.move_id
            WHERE aml.company_id = %s
              AND aa.account_type = 'liability_payable'
              AND aml.reconciled = FALSE
              AND aml.partner_id IS NOT NULL
              AND am.state = 'posted'
              AND (
                  (aml.amount_residual < 0 AND am.move_type = 'in_invoice') -- Open Bills
                  OR 
                  (aml.amount_residual > 0) -- Any available debit (Payment or Journal Entry)
              )
        """, [self.company_id.id])
        return [r[0] for r in self.env.cr.fetchall()]

    def _get_customer_invoice_lines(self, commercial_partner):
        """Unreconciled receivable DEBIT lines from posted out_invoices (FIFO)."""
        return self.env['account.move.line'].search([
            ('account_id.account_type', '=', 'asset_receivable'),
            ('partner_id', 'child_of', commercial_partner.id),
            ('reconciled', '=', False),
            ('amount_residual', '>', 0),
            ('parent_state', '=', 'posted'),
            ('move_id.move_type', '=', 'out_invoice'),
            ('company_id', '=', self.company_id.id),
        ], order='id asc')

    def _get_customer_payment_lines(self, commercial_partner):
        """Unreconciled receivable CREDIT lines from posted inbound payments (FIFO)."""
        return self.env['account.move.line'].search([
            ('account_id.account_type', '=', 'asset_receivable'),
            ('partner_id', 'child_of', commercial_partner.id),
            ('reconciled', '=', False),
            ('amount_residual', '<', 0),
            ('parent_state', '=', 'posted'),
            ('payment_id', '!=', False),
            ('payment_id.payment_type', '=', 'inbound'),
            ('company_id', '=', self.company_id.id),
        ], order='id asc')

    def _get_customer_other_credit_lines(self, commercial_partner):
        """Unreconciled receivable CREDIT lines NOT from formal payments (FIFO).
        E.g. Opening balances, manual journal entries.
        """
        return self.env['account.move.line'].search([
            ('account_id.account_type', '=', 'asset_receivable'),
            ('partner_id', 'child_of', commercial_partner.id),
            ('reconciled', '=', False),
            ('amount_residual', '<', 0),
            ('parent_state', '=', 'posted'),
            ('payment_id', '=', False),
            ('company_id', '=', self.company_id.id),
        ], order='id asc')

    def _get_vendor_bill_lines(self, commercial_partner):
        """Unreconciled payable CREDIT lines from posted in_invoices/bills (FIFO)."""
        return self.env['account.move.line'].search([
            ('account_id.account_type', '=', 'liability_payable'),
            ('partner_id', 'child_of', commercial_partner.id),
            ('reconciled', '=', False),
            ('amount_residual', '<', 0),
            ('parent_state', '=', 'posted'),
            ('move_id.move_type', '=', 'in_invoice'),
            ('company_id', '=', self.company_id.id),
        ], order='id asc')

    def _get_vendor_payment_lines(self, commercial_partner):
        """Unreconciled payable DEBIT lines from posted outbound payments (FIFO)."""
        return self.env['account.move.line'].search([
            ('account_id.account_type', '=', 'liability_payable'),
            ('partner_id', 'child_of', commercial_partner.id),
            ('reconciled', '=', False),
            ('amount_residual', '>', 0),
            ('parent_state', '=', 'posted'),
            ('payment_id', '!=', False),
            ('payment_id.payment_type', '=', 'outbound'),
            ('company_id', '=', self.company_id.id),
        ], order='id asc')

    def _get_vendor_other_debit_lines(self, commercial_partner):
        """Unreconciled payable DEBIT lines NOT from formal payments (FIFO).
        E.g. Opening balances, manual journal entries.
        """
        return self.env['account.move.line'].search([
            ('account_id.account_type', '=', 'liability_payable'),
            ('partner_id', 'child_of', commercial_partner.id),
            ('reconciled', '=', False),
            ('amount_residual', '>', 0),
            ('parent_state', '=', 'posted'),
            ('payment_id', '=', False),
            ('company_id', '=', self.company_id.id),
        ], order='id asc')

    def _reconcile_lines(self, primary_lines, secondary_lines, partner_name):
        """
        Core FIFO engine — works for both customer and vendor.

        primary_lines  : invoice/bill lines to be covered (sorted oldest first)
        secondary_lines: payment lines providing coverage (sorted oldest first)

        Returns number of reconciliation operations performed.
        """
        if not primary_lines or not secondary_lines:
            return 0

        count = 0
        sec_list = list(secondary_lines)
        sec_idx = 0

        for pri in primary_lines:
            if sec_idx >= len(sec_list):
                break

            pri.invalidate_recordset(['amount_residual', 'reconciled'])
            if pri.reconciled or abs(pri.amount_residual) < 0.001:
                continue

            while sec_idx < len(sec_list):
                sec = sec_list[sec_idx]

                sec.invalidate_recordset(['amount_residual', 'reconciled'])
                pri.invalidate_recordset(['amount_residual', 'reconciled'])

                if sec.reconciled or abs(sec.amount_residual) < 0.001:
                    sec_idx += 1
                    continue

                if pri.reconciled or abs(pri.amount_residual) < 0.001:
                    break

                try:
                    (pri | sec).reconcile()
                    count += 1
                except Exception as exc:
                    _logger.warning(
                        'FIFO reconcile failed: partner=%s pri=%d sec=%d — %s',
                        partner_name, pri.id, sec.id, exc,
                    )
                    sec_idx += 1
                    continue

                sec.invalidate_recordset(['amount_residual', 'reconciled'])
                pri.invalidate_recordset(['amount_residual', 'reconciled'])

                if sec.reconciled or abs(sec.amount_residual) < 0.001:
                    sec_idx += 1
                if pri.reconciled or abs(pri.amount_residual) < 0.001:
                    break

        return count

    def _reconcile_customer_partner(self, commercial_partner):
        total = 0
        invoices = self._get_customer_invoice_lines(commercial_partner)
        if not invoices:
            return 0

        total += self._reconcile_lines(
            invoices,
            self._get_customer_payment_lines(commercial_partner),
            commercial_partner.name,
        )

        total += self._reconcile_lines(
            invoices,
            self._get_customer_other_credit_lines(commercial_partner),
            commercial_partner.name,
        )
        return total

    def _reconcile_vendor_partner(self, commercial_partner):
        total = 0
        bills = self._get_vendor_bill_lines(commercial_partner)
        if not bills:
            return 0

        total += self._reconcile_lines(
            bills,
            self._get_vendor_payment_lines(commercial_partner),
            commercial_partner.name,
        )

        total += self._reconcile_lines(
            bills,
            self._get_vendor_other_debit_lines(commercial_partner),
            commercial_partner.name,
        )
        return total


    def action_reconcile(self):
        self.ensure_one()
        total = 0
        processed = 0

        rtype = self.reconcile_type

        if self.partner_id:
            commercial = self.partner_id.commercial_partner_id or self.partner_id
            if rtype in ('customer', 'both'):
                total += self._reconcile_customer_partner(commercial)
            if rtype in ('vendor', 'both'):
                total += self._reconcile_vendor_partner(commercial)
            processed = 1
            if total == 0:
                raise UserError(_(
                    'No new reconciliations for "%s".\n'
                    'Make sure there are posted documents and unreconciled payments.'
                ) % self.partner_id.name)
            msg = _('Reconciled %d line(s) for %s.') % (total, self.partner_id.name)

        else:
            partner_ids = set()
            if rtype in ('customer', 'both'):
                partner_ids.update(self._get_all_customer_ids())
            if rtype in ('vendor', 'both'):
                partner_ids.update(self._get_all_vendor_ids())

            if not partner_ids:
                raise UserError(_('No partners found with open documents and available payments.'))

            for pid in partner_ids:
                partner = self.env['res.partner'].browse(pid)
                c = 0
                if rtype in ('customer', 'both'):
                    c += self._reconcile_customer_partner(partner)
                if rtype in ('vendor', 'both'):
                    c += self._reconcile_vendor_partner(partner)
                if c:
                    total += c
                    processed += 1

            if total == 0:
                raise UserError(_('No new reconciliations for any partner. Everything may already be reconciled.'))
            msg = _('Reconciled %d line(s) across %d partner(s) — oldest to newest.') % (total, processed)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Reconciliation Complete'),
                'message': msg,
                'type': 'success',
                'sticky': False,
            },
        }
