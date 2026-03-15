# Copyright 2018 ForgeFlow, S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class OutstandingStatement(models.AbstractModel):

    _inherit = "report.partner_statement.outstanding_statement"
    def _get_account_display_lines(
        self, company_id, partner_ids, date_start, date_end, account_type
    ):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = tuple(partner_ids)
        # pylint: disable=E8103
        self.env.cr.execute(
            """
        WITH Q1 as (%s),
             Q2 AS (%s),
             Q3 AS (%s)
        SELECT partner_id, currency_id, move_id, date, date_maturity, debit,
                            credit, amount, open_amount, name, ref, blocked
        FROM Q3
        ORDER BY date, date_maturity, move_id"""
            % (
                self._display_lines_sql_q1(partners, date_end, account_type),
                self._display_lines_sql_q2(),
                self._display_lines_sql_q3(company_id),
            )
        )
        for row in self.env.cr.dictfetchall():
            move_id =  self.env['account.move'].search([('name','=',row['move_id'])])
            if move_id:
                row['policy_no']=move_id.policy_no
                row['id_no']=move_id.id_no


            res[row.pop("partner_id")].append(row)
        return res

class ActivityStatement(models.AbstractModel):
    """Model of Activity Statement"""

    _inherit  = "report.partner_statement.activity_statement"
    def _get_account_display_lines(
        self, company_id, partner_ids, date_start, date_end, account_type
    ):
        res = dict(map(lambda x: (x, []), partner_ids))
        partners = tuple(partner_ids)

        # pylint: disable=E8103
        self.env.cr.execute(
            """
        WITH Q1 AS (%s),
             Q2 AS (%s)
        SELECT partner_id, move_id, date, date_maturity, name, ref, debit,
                            credit, amount, blocked, currency_id
        FROM Q2
        ORDER BY date, date_maturity, move_id"""
            % (
                self._display_lines_sql_q1(
                    partners, date_start, date_end, account_type
                ),
                self._display_lines_sql_q2(company_id),
            )
        )
        for row in self.env.cr.dictfetchall():
            move_id = self.env['account.move'].search([('name', '=', row['move_id'])])
            if move_id:
                row['policy_no'] = move_id.policy_no
                row['id_no'] = move_id.id_no

            res[row.pop("partner_id")].append(row)
        return res