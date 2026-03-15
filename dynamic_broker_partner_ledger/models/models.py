from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date
import calendar
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import json
import io
from odoo.tools import date_utils
import base64

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

DATE_DICT = {
    '%m/%d/%Y' : 'mm/dd/yyyy',
    '%Y/%m/%d' : 'yyyy/mm/dd',
    '%m/%d/%y' : 'mm/dd/yy',
    '%d/%m/%Y' : 'dd/mm/yyyy',
    '%d/%m/%y' : 'dd/mm/yy',
    '%d-%m-%Y' : 'dd-mm-yyyy',
    '%d-%m-%y' : 'dd-mm-yy',
    '%m-%d-%Y' : 'mm-dd-yyyy',
    '%m-%d-%y' : 'mm-dd-yy',
    '%Y-%m-%d' : 'yyyy-mm-dd',
    '%f/%e/%Y' : 'm/d/yyyy',
    '%f/%e/%y' : 'm/d/yy',
    '%e/%f/%Y' : 'd/m/yyyy',
    '%e/%f/%y' : 'd/m/yy',
    '%f-%e-%Y' : 'm-d-yyyy',
    '%f-%e-%y' : 'm-d-yy',
    '%e-%f-%Y' : 'd-m-yyyy',
    '%e-%f-%y' : 'd-m-yy'
}

FETCH_RANGE = 2000

class InsPartnerLedger(models.TransientModel):
    _inherit = "ins.partner.ledger"

    def build_detailed_move_lines(self, offset=0, partner=0, fetch_range=FETCH_RANGE):

        cr = self.env.cr
        data = self.get_filters(default_filters={})
        offset_count = offset * fetch_range
        count = 0
        opening_balance = 0

        currency_id = self.env.company.currency_id

        WHERE = self.build_where_clause()

        WHERE_INIT = WHERE + " AND l.date < '%s'" % data.get('date_from')
        WHERE_INIT += " AND l.partner_id = %s" % partner

        WHERE_CURRENT = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
            'date_to')
        WHERE_CURRENT += " AND p.id = %s" % partner

        if data.get('initial_balance'):
            WHERE_FULL = WHERE + " AND l.date <= '%s'" % data.get('date_to')
        else:
            WHERE_FULL = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                'date_to')
        WHERE_FULL += " AND p.id = %s" % partner

        ORDER_BY_CURRENT = 'l.date'

        move_lines = []
        if data.get('initial_balance'):
            sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                    --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_INIT
            cr.execute(sql)
            row = cr.dictfetchone()
            opening_balance += row.get('balance')

        sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                    --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                    GROUP BY l.date, l.move_id
                    ORDER BY %s
                    OFFSET %s ROWS
                    FETCH FIRST %s ROWS ONLY
                ''') % (WHERE_CURRENT, ORDER_BY_CURRENT, 0, offset_count)
        cr.execute(sql)
        running_balance_list = cr.fetchall()
        for running_balance in running_balance_list:
            opening_balance += running_balance[0]
        sql = ('''
            SELECT COUNT(*)
            FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
            WHERE %s
        ''') % (WHERE_CURRENT)
        cr.execute(sql)
        count = cr.fetchone()[0]
        if (int(offset_count / fetch_range) == 0) and data.get('initial_balance'):
            sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                    --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_INIT
            cr.execute(sql)
            for row in cr.dictfetchall():
                row['move_name'] = 'Initial Balance'
                row['partner_id'] = partner
                row['company_currency_id'] = currency_id.id
                move_lines.append(row)
        lang = self.env.user.lang
        account_name = f"COALESCE(a.name->>'{lang}')" if \
            self.pool['account.account'].name.translate else 'a.name'
        sql = (f'''
                SELECT
                    l.id AS lid,
                    l.account_id AS account_id,
                    l.partner_id AS partner_id,
                    l.date AS ldate,
                    j.code AS lcode,
                    l.currency_id,
                    l.amount_currency,
                    --l.ref AS lref,
                    l.name AS lname,
                    m.id AS move_id,
                    m.name AS move_name,
                    c.symbol AS currency_symbol,
                    c.position AS currency_position,
                    c.rounding AS currency_precision,
                    cc.id AS company_currency_id,
                    cc.symbol AS company_currency_symbol,
                    cc.rounding AS company_currency_precision,
                    cc.position AS company_currency_position,
                    m.policy_no as policy_no,
                    m.id_no as id_no,
                    p.name AS partner_name,
                     a.name AS account_name,
                    COALESCE(l.debit,0) AS debit,
                    COALESCE(l.credit,0) AS credit,
                    COALESCE(l.debit - l.credit,0) AS balance,
                    COALESCE(l.amount_currency,0) AS amount_currency
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                WHERE %s
                GROUP BY l.id, l.partner_id,a.name, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.name, m.id, m.name, c.rounding, cc.id, cc.rounding, cc.position, c.position, c.symbol, cc.symbol, p.name
                ORDER BY %s
                OFFSET %s ROWS
                FETCH FIRST %s ROWS ONLY
            ''') % (WHERE_CURRENT, ORDER_BY_CURRENT, offset_count, fetch_range)
        cr.execute(sql)

        for row in cr.dictfetchall():
            current_balance = row['balance']
            row['balance'] = opening_balance + current_balance
            opening_balance += current_balance
            row['initial_bal'] = False
            move_lines.append(row)

        if ((count - offset_count) <= fetch_range) and data.get('initial_balance'):
            sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                    --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_FULL
            cr.execute(sql)
            for row in cr.dictfetchall():
                row['move_name'] = 'Ending Balance'
                row['partner_id'] = partner
                row['company_currency_id'] = currency_id.id
                move_lines.append(row)
        return count, offset_count, move_lines
    def process_data(self):

        '''
        It is the method for showing summary details of each accounts. Just basic details to show up
        Three sections,
        1. Initial Balance
        2. Current Balance
        3. Final Balance
        :return:
        '''
        if self.summary:
            self.initial_balance=False
            self.include_details=False
        cr = self.env.cr

        data = self.get_filters(default_filters={})

        WHERE = self.build_where_clause(data)

        partner_company_domain = [('parent_id', '=', False),
                                  '|',
                                  ('company_id', '=', self.env.company.id),
                                  ('company_id', '=', False)]
        if self.partner_category_ids:
            partner_company_domain.append(('category_id','in',self.partner_category_ids.ids))

        if data.get('partner_ids', []):
            partner_ids = self.env['res.partner'].browse(data.get('partner_ids'))
        else:
            partner_ids = self.env['res.partner'].search(partner_company_domain)

        move_lines = {
            x.id: {
                'name': x.name,
                'code': x.id,
                'company_currency_id': 0,
                'company_currency_symbol': 'AED',
                'company_currency_precision': 0.0100,
                'company_currency_position': 'after',
                'id': x.id,
                'lines': []
            } for x in partner_ids
        }
        for partner in partner_ids:

            currency = partner.company_id.currency_id or self.env.company.currency_id
            symbol = currency.symbol
            rounding = currency.rounding
            position = currency.position

            opening_balance = 0.0

            WHERE_INIT = WHERE + " AND l.date < '%s'" % data.get('date_from')
            WHERE_INIT += " AND l.partner_id = %s" % partner.id
            ORDER_BY_CURRENT = 'l.date'

            if data.get('initial_balance'):
                sql = ('''
                    SELECT 
                        COALESCE(SUM(l.debit),0) AS debit, 
                        COALESCE(SUM(l.credit),0) AS credit, 
                        COALESCE(SUM(l.debit - l.credit),0) AS balance
                    FROM account_move_line l
                    JOIN account_move m ON (l.move_id=m.id)
                    JOIN account_account a ON (l.account_id=a.id)
                    --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                    --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                    LEFT JOIN res_currency c ON (l.currency_id=c.id)
                    LEFT JOIN res_partner p ON (l.partner_id=p.id)
                    JOIN account_journal j ON (l.journal_id=j.id)
                    WHERE %s
                ''') % WHERE_INIT
                cr.execute(sql)
                for row in cr.dictfetchall():
                    row['move_name'] = 'Initial Balance'
                    row['partner_id'] = partner.id
                    row['initial_bal'] = True
                    row['ending_bal'] = False
                    opening_balance += row['balance']
                    move_lines[partner.id]['lines'].append(row)
            WHERE_CURRENT = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                'date_to')
            WHERE_CURRENT += " AND p.id = %s" % partner.id
            lang = self.env.user.lang
            account_name = f"COALESCE(a.name->>'{lang}')" if \
                self.pool['account.account'].name.translate else 'a.name'
            sql = (f'''
                SELECT
                    l.id AS lid,
                    l.date AS ldate,
                    j.code AS lcode,
                    {account_name} AS account_name,
                    m.name AS move_name,
                     m.policy_no as policy_no,
                    m.id_no as id_no,
                    l.name AS lname,
                    COALESCE(l.debit,0) AS debit,
                    COALESCE(l.credit,0) AS credit,
                    COALESCE(l.balance,0) AS balance,
                    COALESCE(l.amount_currency,0) AS balance_currency
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_currency cc ON (l.company_currency_id=cc.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                WHERE %s
                --GROUP BY l.id, l.account_id, l.date, j.code, l.currency_id, l.amount_currency, l.ref, l.name, m.id, m.name, c.rounding, cc.rounding, cc.position, c.position, c.symbol, cc.symbol, p.name
                ORDER BY %s
            ''') % (WHERE_CURRENT, ORDER_BY_CURRENT)
            cr.execute(sql)
            current_lines = cr.dictfetchall()
            for row in current_lines:
                row['initial_bal'] = False
                row['ending_bal'] = False

                current_balance = row['balance']
                row['balance'] = opening_balance + current_balance
                opening_balance += current_balance
                row['initial_bal'] = False

                move_lines[partner.id]['lines'].append(row)
            if data.get('initial_balance'):
                WHERE_FULL = WHERE + " AND l.date <= '%s'" % data.get('date_to')
            else:
                WHERE_FULL = WHERE + " AND l.date >= '%s'" % data.get('date_from') + " AND l.date <= '%s'" % data.get(
                    'date_to')
            WHERE_FULL += " AND p.id = %s" % partner.id
            sql = ('''
                SELECT 
                    COALESCE(SUM(l.debit),0) AS debit, 
                    COALESCE(SUM(l.credit),0) AS credit, 
                    COALESCE(SUM(l.debit - l.credit),0) AS balance
                FROM account_move_line l
                JOIN account_move m ON (l.move_id=m.id)
                JOIN account_account a ON (l.account_id=a.id)
                --LEFT JOIN account_account_type AS ty ON a.user_type_id = ty.id
                --LEFT JOIN account_analytic_account anl ON (l.analytic_account_id=anl.id)
                LEFT JOIN res_currency c ON (l.currency_id=c.id)
                LEFT JOIN res_partner p ON (l.partner_id=p.id)
                JOIN account_journal j ON (l.journal_id=j.id)
                WHERE %s
            ''') % WHERE_FULL
            cr.execute(sql)
            for row in cr.dictfetchall():
                if (data.get('display_accounts') == 'balance_not_zero' and currency.is_zero(row['debit'] - row['credit']))\
                        or (data.get('balance_less_than_zero') and (row['debit'] - row['credit']) > 0)\
                        or (data.get('balance_greater_than_zero') and (row['debit'] - row['credit']) < 0):
                    move_lines.pop(partner.id, None)
                else:
                    row['ending_bal'] = False if self.summary else True
                    row['initial_bal'] = False
                    move_lines[partner.id]['lines'].append(row)
                    move_lines[partner.id]['debit'] = row['debit']
                    move_lines[partner.id]['credit'] = row['credit']
                    move_lines[partner.id]['balance'] = row['balance']
                    move_lines[partner.id]['company_currency_id'] = currency.id
                    move_lines[partner.id]['company_currency_symbol'] = symbol
                    move_lines[partner.id]['company_currency_precision'] = rounding
                    move_lines[partner.id]['company_currency_position'] = position
                    move_lines[partner.id]['count'] = len(current_lines)
                    move_lines[partner.id]['pages'] = self.get_page_list(len(current_lines))
                    move_lines[partner.id]['single_page'] = True if len(current_lines) <= FETCH_RANGE else False
        return move_lines
    def action_xlsx(self):
        data = self.read()[0]
        # Initialize
        #############################################################
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Partner Ledger')
        sheet.set_zoom(90)
        sheet_2 = workbook.add_worksheet('Filters')
        sheet_2.protect()

        # Get record and data
        record = self.env['ins.partner.ledger'].browse(data.get('id', [])) or False
        filter, account_lines = record.get_report_datas()

        # Formats
        ############################################################
        sheet.set_column(0, 0, 12)
        sheet.set_column(1, 1, 12)
        sheet.set_column(2, 2, 30)
        sheet.set_column(3, 3, 18)
        sheet.set_column(4, 4, 30)
        sheet.set_column(5, 5, 13)
        sheet.set_column(6, 6, 13)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 15)
        sheet.set_column(9, 9, 15)

        sheet_2.set_column(0, 0, 35)
        sheet_2.set_column(1, 1, 25)
        sheet_2.set_column(2, 2, 25)
        sheet_2.set_column(3, 3, 25)
        sheet_2.set_column(4, 4, 25)
        sheet_2.set_column(5, 5, 25)
        sheet_2.set_column(6, 6, 25)

        sheet.freeze_panes(4, 0)

        # sheet.screen_gridlines = False
        # sheet_2.screen_gridlines = False
        sheet_2.protect()

        format_title = workbook.add_format({
            'bold': True,
            'align': 'center',
            'font_size': 12,
            'font': 'Arial',
            'border': False
        })
        format_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'border': True
        })
        content_header = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'border': True,
            'font': 'Arial',
        })
        content_header_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'border': True,
            'align': 'center',
            'font': 'Arial',
        })
        line_header = workbook.add_format({
            'bold': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'bottom': True,
            'font': 'Arial',
        })
        line_header_light = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'text_wrap': True,
            'font': 'Arial',
            'valign': 'top',
            'border': True
        })
        line_header_light_date = workbook.add_format({
            'bold': False,
            'font_size': 10,
            'align': 'center',
            'font': 'Arial',
            'border':True
        })
        line_header_light_initial = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'bottom': True,
            'font': 'Arial',
            'valign': 'top'
        })
        line_header_light_initial_bold = workbook.add_format({
            'bold': True,
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'bottom': True,
            'font': 'Arial',
            'valign': 'top'
        })
        line_header_light_ending = workbook.add_format({
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'top': True,
            'font': 'Arial',
            'valign': 'top'
        })
        line_header_light_ending_bold = workbook.add_format({
            'bold': True,
            'italic': True,
            'font_size': 10,
            'align': 'center',
            'bottom': True,
            'font': 'Arial',
            'valign': 'top'
        })
        lang = self.env.user.lang
        lang_id = self.env['res.lang'].search([('code', '=', lang)])[0]
        currency_id = self.env.user.company_id.currency_id
        line_header.num_format = currency_id.excel_format
        line_header_light.num_format = currency_id.excel_format
        line_header_light_initial.num_format = currency_id.excel_format
        line_header_light_ending.num_format = currency_id.excel_format
        line_header_light_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')
        content_header_date.num_format = DATE_DICT.get(lang_id.date_format, 'dd/mm/yyyy')

        # Write data
        ################################################################
        row_pos_2 = 0
        row_pos = 0
        sheet.merge_range(0, 0, 0, 8, 'Partner Ledger' + ' - ' + data['company_id'][1], format_title)

        # Write filters
        sheet_2.write(row_pos_2, 0, _('Date from'), format_header)
        datestring = fields.Date.from_string(str(filter['date_from'])).strftime(lang_id.date_format)
        sheet_2.write(row_pos_2, 1, datestring or '', content_header_date)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Date to'), format_header)
        datestring = fields.Date.from_string(str(filter['date_to'])).strftime(lang_id.date_format)
        sheet_2.write(row_pos_2, 1, datestring or '', content_header_date)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Target moves'), format_header)
        sheet_2.write(row_pos_2, 1, filter['target_moves'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Display accounts'), format_header)
        sheet_2.write(row_pos_2, 1, filter['display_accounts'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Reconciled'), format_header)
        sheet_2.write(row_pos_2, 1, filter['reconciled'], content_header)
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Initial Balance'), format_header)
        sheet_2.write(row_pos_2, 1, filter['initial_balance'], content_header)
        row_pos_2 += 1
        # Journals
        row_pos_2 += 2
        sheet_2.write(row_pos_2, 0, _('Journals'), format_header)
        j_list = ', '.join([lt or '' for lt in filter.get('journals')])
        sheet_2.write(row_pos_2, 1, j_list, content_header)
        # Partners
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Partners'), format_header)
        p_list = ', '.join([lt or '' for lt in filter.get('partners')])
        sheet_2.write(row_pos_2, 1, p_list, content_header)
        # Partner Tags
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Partner Tag'), format_header)
        p_list = ', '.join([lt or '' for lt in filter.get('categories')])
        sheet_2.write(row_pos_2, 1, p_list, content_header)
        # Accounts
        row_pos_2 += 1
        sheet_2.write(row_pos_2, 0, _('Accounts'), format_header)
        a_list = ', '.join([lt or '' for lt in filter.get('accounts')])
        sheet_2.write(row_pos_2, 1, a_list, content_header)
        # Write Ledger details
        row_pos += 3
        if filter.get('include_details', False):
            sheet.write(row_pos, 0, _('Date'),
                                    format_header)
            sheet.write(row_pos, 1, _('JRNL'),
                                    format_header)
            sheet.write(row_pos, 2, _('Account'),
                                    format_header)
            sheet.write(row_pos, 3, _('Policy No'),
                        format_header)
            sheet.write(row_pos, 4, _('ID No'),
                        format_header)
            # sheet.write(row_pos, 3, _('Ref'),
            #                         format_header)
            sheet.write(row_pos, 5, _('Move'),
                                    format_header)
            sheet.write(row_pos, 6, _('Entry Label'),
                                    format_header)
            sheet.write(row_pos, 7, _('Debit'),
                                    format_header)
            sheet.write(row_pos, 8, _('Credit'),
                                  format_header)
            sheet.write(row_pos, 9, _('Balance'),
                                    format_header)
        else:
            sheet.merge_range(row_pos, 0, row_pos, 6, _('Partner'), format_header)
            sheet.write(row_pos, 7, _('Debit'),
                                    format_header)
            sheet.write(row_pos, 8, _('Credit'),
                                    format_header)
            sheet.write(row_pos, 9, _('Balance'),
                                    format_header)

        if account_lines:
            for line in account_lines:
                row_pos += 1
                sheet.merge_range(row_pos, 0, row_pos, 6, account_lines[line].get('name'), line_header)
                sheet.write(row_pos, 7, float(account_lines[line].get('debit')), line_header)
                sheet.write(row_pos, 8, float(account_lines[line].get('credit')), line_header)
                sheet.write(row_pos, 9, float(account_lines[line].get('balance')), line_header)

                if filter.get('include_details', False):

                    count, offset, sub_lines = record.build_detailed_move_lines(offset=0, partner=line,
                                                                                     fetch_range=1000000)

                    for sub_line in sub_lines:
                        if sub_line.get('move_name') == 'Initial Balance':
                            row_pos += 1
                            sheet.write(row_pos, 6, sub_line.get('move_name'),
                                                    line_header_light_initial_bold)
                            sheet.write(row_pos, 7, '{:,.2f}'.format(float(sub_line.get('debit'))),
                                                    line_header_light_initial)
                            sheet.write(row_pos, 8, '{:,.2f}'.format(float(sub_line.get('credit'))),
                                                    line_header_light_initial)
                            sheet.write(row_pos, 9, '{:,.2f}'.format(float(sub_line.get('balance'))),
                                                    line_header_light_initial)
                        elif sub_line.get('move_name') not in ['Initial Balance','Ending Balance']:
                            row_pos += 1
                            datestring = fields.Date.from_string(str(sub_line.get('ldate'))).strftime(
                                lang_id.date_format)
                            sheet.write(row_pos, 0, datestring or '',
                                                    line_header_light_date)
                            sheet.write(row_pos, 1, sub_line.get('lcode'),
                                                    line_header_light)
                            sheet.write(row_pos, 2, str(sub_line.get('account_name')) or '',
                                                    line_header_light)
                            sheet.write(row_pos, 3, str(sub_line.get('policy_no')) if sub_line.get('policy_no') else '' ,
                                        line_header_light)
                            sheet.write(row_pos, 4, str(sub_line.get('id_no')) if sub_line.get('id_no') else '' ,
                                        line_header_light)
                            # sheet.write(row_pos, 3, sub_line.get('lref') or '',
                            #                         line_header_light)
                            sheet.write(row_pos, 5, sub_line.get('move_name'),
                                                    line_header_light)
                            sheet.write(row_pos, 6, sub_line.get('lname') or '',
                                                    line_header_light)
                            sheet.write(row_pos, 7,
                                        '{:,.2f}'.format( float(sub_line.get('debit'))),line_header_light)
                            sheet.write(row_pos, 8,
                                                    '{:,.2f}'.format(float(sub_line.get('credit'))),line_header_light)
                            sheet.write(row_pos, 9,
                                                    '{:,.2f}'.format(float(sub_line.get('balance'))),line_header_light)
                        else: # Ending Balance
                            row_pos += 1
                            sheet.write(row_pos, 6, sub_line.get('move_name'),
                                                    line_header_light_ending_bold)
                            sheet.write(row_pos, 7, '{:,.2f}'.format(float(account_lines[line].get('debit'))),
                                                    line_header_light_ending)
                            sheet.write(row_pos, 8, '{:,.2f}'.format(float(account_lines[line].get('credit'))),
                                                    line_header_light_ending)
                            sheet.write(row_pos, 9, '{:,.2f}'.format(float(account_lines[line].get('balance'))),
                                                    line_header_light_ending)

        # Close and return
        #################################################################
        workbook.close()
        output.seek(0)
        result = base64.b64encode(output.read())
        report_id = self.env['common.xlsx.out'].sudo().create({'filedata': result, 'filename': 'PartnerLedger.xls'})

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_document?model=common.xlsx.out&field=filedata&id=%s&filename=%s.xlsx' % (
                report_id.id, 'Partner Ledger'),
            'target': 'new',
        }

        output.close()
