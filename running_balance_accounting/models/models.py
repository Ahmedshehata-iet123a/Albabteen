# -*- coding: utf-8 -*-
import ast
from babel.dates import format_datetime, format_date
from collections import defaultdict
from datetime import datetime, timedelta
import json
import random

from odoo import models, api, _, fields
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.release import version
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang



from odoo import models, fields, api

class account_journal(models.Model):
    _inherit = "account.journal"

    def _fill_bank_cash_dashboard_data(self, dashboard_data):
        """Populate all bank and cash journal's data dict with relevant information for the kanban card."""
        bank_cash_journals = self.filtered(lambda journal: journal.type in ('bank', 'cash'))
        if not bank_cash_journals:
            return

        # Number to reconcile
        self._cr.execute("""
               SELECT st_line_move.journal_id,
                      COUNT(st_line.id)
                 FROM account_bank_statement_line st_line
                 JOIN account_move st_line_move ON st_line_move.id = st_line.move_id
                WHERE st_line_move.journal_id IN %s
                  AND NOT st_line.is_reconciled
                  AND st_line_move.to_check IS NOT TRUE
                  AND st_line_move.state = 'posted'
             GROUP BY st_line_move.journal_id
           """, [tuple(bank_cash_journals.ids)])
        number_to_reconcile = {
            journal_id: count
            for journal_id, count in self.env.cr.fetchall()
        }

        # Last statement
        self.env.cr.execute("""
               SELECT journal.id, statement.id
                 FROM account_journal journal
            LEFT JOIN LATERAL (
                         SELECT id
                           FROM account_bank_statement
                          WHERE journal_id = journal.id
                       ORDER BY first_line_index DESC
                          LIMIT 1
                      ) statement ON TRUE
                WHERE journal.id = ANY(%s)
           """, [self.ids])
        last_statements = {journal_id: statement_id for journal_id, statement_id in self.env.cr.fetchall()}
        self.env['account.bank.statement'].browse(i for i in last_statements.values() if i).mapped(
            'balance_end_real')  # prefetch

        outstanding_pay_account_balances = bank_cash_journals._get_journal_dashboard_outstanding_payments()

        # To check
        to_check = {
            res['journal_id'][0]: (res['amount'], res['journal_id_count'])
            for res in self.env['account.bank.statement.line'].read_group(
                domain=[
                    ('journal_id', 'in', bank_cash_journals.ids),
                    ('move_id.to_check', '=', True),
                    ('move_id.state', '=', 'posted'),
                ],
                fields=['amount'],
                groupby=['journal_id'],
            )
        }

        for journal in bank_cash_journals:
            last_statement = self.env['account.bank.statement'].browse(last_statements.get(journal.id))
            currency = journal.currency_id or journal.company_id.currency_id
            has_outstanding, outstanding_pay_account_balance = outstanding_pay_account_balances[journal.id]
            to_check_balance, number_to_check = to_check.get(journal.id, (0, 0))

            dashboard_data[journal.id].update({
                'number_to_check': number_to_check,
                'to_check_balance': currency.format(to_check_balance),
                'number_to_reconcile': number_to_reconcile.get(journal.id, 0),
                'account_balance': currency.format(journal.default_account_id.current_balance),
                'has_at_least_one_statement': bool(last_statement),
                'nb_lines_bank_account_balance': bool(journal.has_statement_lines),
                'outstanding_pay_account_balance': currency.format(outstanding_pay_account_balance),
                'nb_lines_outstanding_pay_account_balance': has_outstanding,
                'last_balance': currency.format(last_statement.balance_end_real),
                'bank_statements_source': journal.bank_statements_source,
                'is_sample_data': journal.has_statement_lines,
            })
