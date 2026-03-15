from odoo import fields, models, api, _
from datetime import date, timedelta, datetime
from odoo.tools.misc import xlwt
from PIL import Image, ImageColor
from io import BytesIO
import itertools
from datetime import date

# from webcolors import hex_to_rgb ,rgb_to_hex
# import webcolors

import io
import base64


class purchase_print_excel(models.TransientModel):
    _name = 'partner.ledger.customer'
    date_from = fields.Date()
    date_to = fields.Date()
    partner_id = fields.Many2many(
        comodel_name='res.partner',
        string='Partners')

    def print_excel(self):

        if not self.partner_id:
            filename = 'Partner Ledger' + '.xls'
        if len(self.partner_id):
            for rec in self.partner_id:
                filename = rec.name + '.xls'

        workbook = xlwt.Workbook()

        # ids = self.env.context['active_ids']
        # order_lines = self.env['purchase.order.line'].browse(ids)

        worksheet = workbook.add_sheet(filename)
        # format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        font = xlwt.Font()
        font.bold = True
        for_left = xlwt.easyxf(
            "font: bold 1, color black; borders: top double, bottom double, left double, right double; align: horiz left")
        multi_record = xlwt.easyxf(
            "font: color black; borders: top double, bottom double, left double, right double; align: horiz center")
        multi_record_center = xlwt.easyxf(
            "font: height 200, bold True, name Arial; align: horiz center, vert center; borders: top double, bottom double, left double, right double ;")
        style1 = xlwt.easyxf(num_format_str='D-MMM-YY', )
        for_right = xlwt.easyxf(
            "font: bold 1, color black; borders: top double; align: horiz center")
        for_left_noborder = xlwt.easyxf(
            "font: bold 1, color black; borders: top double; align: horiz center")
        for_right_noborder = xlwt.easyxf(
            "font: bold 1, color black; align: horiz center")

        data_table = xlwt.easyxf(
            "font: bold 1, color black; borders: top double, bottom double, left double, right double; align: horiz left;pattern: pattern solid, fore_colour Blue ;"
        )
        GREEN_TABLE_HEADER = xlwt.easyxf(
            'font: bold 1, name Tahoma, height 250;'
            'align: vertical center, horizontal center, wrap on;'
            'borders: top double, bottom double, left double, right double;'
        )
        Employee_Details = xlwt.easyxf(
            'font: bold 1, name Tahoma, height 250, color black;'
            'align: vertical center, horizontal left, wrap on;'
            'borders: top double, bottom double, left double, right double;'
        )
        manager_Details = xlwt.easyxf(
            'font: bold 1, name Tahoma, height 250, color blue;'
            'align: vertical center, horizontal left, wrap on;'
            'borders: top double, bottom double, left double, right double;'
        )
        comment = xlwt.easyxf(
            'font: bold 1, name Tahoma, height 250, color blue;'
            'align: vertical center, horizontal left, wrap on;'

        )
        style = xlwt.easyxf(
            'font:height 400, bold True, name Arial; align: horiz center, vert center;borders: top medium,right medium,bottom medium,left medium')

        alignment = xlwt.Alignment()  # Create Alignment
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        style = xlwt.easyxf('align: wrap yes')
        style.num_format_str = '0.00'
        # worksheet.add_table('B1:F4')

        roww = 4
        current_date = fields.Datetime.now().date()

        worksheet.write(roww, 5, 'Partner', multi_record_center)
        worksheet.write(roww, 6, 'JRNL', multi_record_center)
        worksheet.write(roww, 7, 'POLICY NO', multi_record_center)
        worksheet.write(roww, 8, 'ID NO', multi_record_center)
        worksheet.write(roww, 9, 'Account', multi_record_center)
        worksheet.write(roww, 10, 'Ref', multi_record_center)
        worksheet.write(roww, 11, 'Due Date', multi_record_center)
        worksheet.write(roww, 12, 'Matching Number', multi_record_center)
        worksheet.write(roww, 13, 'Debit', multi_record_center)
        worksheet.write(roww, 14, 'Credit', multi_record_center)
        worksheet.write(roww, 15, 'Amount Currency', multi_record_center)
        worksheet.write(roww, 16, 'Balance', multi_record_center)
        year = 2023
        partner_ids = self.env['res.partner'].search([])
        unfolded_lines = []
        date_design = {}
        if self.partner_id:
            partner_ids = self.env['res.partner'].search([('id', 'in', self.partner_id.ids)])
        current_year = date.today().year
        current_year = 2022
        if not self.date_from and not self.date_to:
            date_design = {
                "string": str(current_year),  ##'From 08/07/2022\nto  12/31/2023'
                "period_type": "fiscalyear",  ## empty custpom
                "mode": "range",  ##custom
                "date_from": "%s-01-01" % (str(current_year)),
                "date_to": "%s-12-31" % str(current_year),
                "filter": "this_year",  ##custom
            }
        else:
            print(">>>>>>>>>>>..","From %s\nto %s" % (self.date_from.strftime('%Y-%m-%d'), self.date_to.strftime('%Y-%m-%d')))
            date_design = {
                "string": "From %s to %s" % (self.date_from.strftime('%Y-%m-%d'), self.date_to.strftime('%Y-%m-%d')),
                ##'From 08/07/2022\nto  12/31/2023'
                ## empty custpom
                'period_type' : 'range',
                "mode": "custom",  ##custom
                "date_from":self.date_from.strftime('%Y-%m-%d'),
                "date_to": self.date_to.strftime('%Y-%m-%d'),
                "filter": "custom",  ##custom
            }
            date_design={'string': 'From 12/26/2021\nto  12/31/2023', 'period_type': 'custom', 'mode': 'range', 'date_from': '2021-12-26', 'date_to': '2023-12-31', 'filter': 'custom'}

        unfold = '-res.partner-'
        for l in partner_ids:
            unfolded_lines.append(unfold + str(l.id))
        # options = {
        #     "unfolded_lines": unfolded_lines,
        #     "available_variants": [{"id": 14, "name": "Partner Ledger", "country_id": False}],
        #     "report_id": 14,
        #     "allow_domestic": True,
        #     "fiscal_position": "all",
        #     "available_vat_fiscal_positions": [],
        #     "date": date_design,
        #     "available_horizontal_groups": [],
        #     "selected_horizontal_group_id": None,
        #     "account_type": [
        #         {"id": "trade_receivable", "name": "Receivable", "selected": True},
        #         {
        #             "id": "non_trade_receivable",
        #             "name": "Non Trade Receivable",
        #             "selected": False,
        #         },
        #         {"id": "trade_payable", "name": "Payable", "selected": True},
        #         {"id": "non_trade_payable", "name": "Non Trade Payable", "selected": False},
        #     ],
        #     "account_display_name": "Trade Partners",
        #     "all_entries": False,
        #     "buttons": [
        #         {
        #             "name": "PDF",
        #             "sequence": 10,
        #             "action": "export_file",
        #             "action_param": "export_to_pdf",
        #             "file_export_type": "PDF",
        #         },
        #         {
        #             "name": "XLSX",
        #             "sequence": 20,
        #             "action": "export_file",
        #             "action_param": "export_to_xlsx",
        #             "file_export_type": "XLSX",
        #         },
        #         {"name": "Save", "sequence": 100, "action": "open_report_export_wizard"},
        #     ],
        #     "partner": True,
        #     "partner_ids": [],
        #     "partner_categories": [],
        #     "selected_partner_ids": [],
        #     "selected_partner_categories": [],
        #     "unreconciled": False,
        #     "search_bar": True,
        #     "unfold_all": False,
        #     "column_headers": [
        #         [
        #             {
        #                 "name": "2023",
        #                 "forced_options": {
        #                     "date": {
        #                         "string": "2023",
        #                         "period_type": "fiscalyear",
        #                         "mode": "range",
        #                         "date_from": "2023-01-01",
        #                         "date_to": "2023-12-31",
        #                         "filter": "this_year",
        #                     }
        #                 },
        #             }
        #         ]
        #     ],
        #     "columns": [
        #         {
        #             "name": "JRNL",
        #             "column_group_key": "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))",
        #             "expression_label": "journal_code",
        #             "sortable": False,
        #             "figure_type": "none",
        #             "blank_if_zero": True,
        #             "style": "text-align: center; white-space: nowrap;",
        #         },
        #         {
        #             "name": "Account",
        #             "column_group_key": "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))",
        #             "expression_label": "account_code",
        #             "sortable": False,
        #             "figure_type": "none",
        #             "blank_if_zero": True,
        #             "style": "text-align: center; white-space: nowrap;",
        #         },
        #         {
        #             "name": "Ref",
        #             "column_group_key": "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))",
        #             "expression_label": "ref",
        #             "sortable": False,
        #             "figure_type": "none",
        #             "blank_if_zero": True,
        #             "style": "text-align: center; white-space: nowrap;",
        #         },
        #         {
        #             "name": "Due Date",
        #             "column_group_key": "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))",
        #             "expression_label": "date_maturity",
        #             "sortable": False,
        #             "figure_type": "none",
        #             "blank_if_zero": True,
        #             "style": "text-align: center; white-space: nowrap;",
        #         },
        #         {
        #             "name": "Matching Number",
        #             "column_group_key": "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))",
        #             "expression_label": "matching_number",
        #             "sortable": False,
        #             "figure_type": "none",
        #             "blank_if_zero": True,
        #             "style": "text-align: center; white-space: nowrap;",
        #         },
        #         {
        #             "name": "Debit",
        #             "column_group_key": "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))",
        #             "expression_label": "debit",
        #             "sortable": False,
        #             "figure_type": "monetary",
        #             "blank_if_zero": True,
        #             "style": "text-align: center; white-space: nowrap;",
        #         },
        #         {
        #             "name": "Credit",
        #             "column_group_key": "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))",
        #             "expression_label": "credit",
        #             "sortable": False,
        #             "figure_type": "monetary",
        #             "blank_if_zero": True,
        #             "style": "text-align: center; white-space: nowrap;",
        #         },
        #         {
        #             "name": "Amount Currency",
        #             "column_group_key": "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))",
        #             "expression_label": "amount_currency",
        #             "sortable": False,
        #             "figure_type": "monetary",
        #             "blank_if_zero": True,
        #             "style": "text-align: center; white-space: nowrap;",
        #         },
        #         {
        #             "name": "Balance",
        #             "column_group_key": "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))",
        #             "expression_label": "balance",
        #             "sortable": False,
        #             "figure_type": "monetary",
        #             "blank_if_zero": False,
        #             "style": "text-align: center; white-space: nowrap;",
        #         },
        #         {
        #             "name": "POLICY NO",
        #             "column_group_key": "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))",
        #             "expression_label": "policy_no",
        #             "sortable": False,
        #             "figure_type": "none",
        #             "blank_if_zero": True,
        #             "style": "text-align: center; white-space: nowrap;",
        #         },
        #         {
        #             "name": "ID NO",
        #             "column_group_key": "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))",
        #             "expression_label": "id_no",
        #             "sortable": False,
        #             "figure_type": "none",
        #             "blank_if_zero": True,
        #             "style": "text-align: center; white-space: nowrap;",
        #         },
        #     ],
        #     "column_groups": {
        #         "(('forced_options', (('date', (('date_from', '2023-01-01'), ('date_to', '2023-12-31'), ('filter', 'this_year'), ('mode', 'range'), ('period_type', 'fiscalyear'), ('string', '2023'))),)), ('horizontal_groupby_element', ()))": {
        #             "forced_options": {
        #                 "date": {
        #                     "string": "2023",
        #                     "period_type": "fiscalyear",
        #                     "mode": "range",
        #                     "date_from": "2023-01-01",
        #                     "date_to": "2023-12-31",
        #                     "filter": "this_year",
        #                 }
        #             },
        #             "forced_domain": [],
        #         }
        #     },
        #     "show_debug_column": False,
        #     "show_growth_comparison": None,
        #     "order_column": None,
        #     "hierarchy": False,
        #     "display_hierarchy_filter": False,
        #     "forced_domain": [
        #         "!",
        #         "&",
        #         "&",
        #         "&",
        #         ("credit", "=", 0.0),
        #         ("debit", "=", 0.0),
        #         ("amount_currency", "!=", 0.0),
        #         ("journal_id", "in", [4]),
        #     ],
        #     "unposted_in_period": True,
        # }
        options ={'unfolded_lines': ['-res.partner-14', '-res.partner-10'], 'available_variants': [{'id': 14, 'name': 'Partner Ledger', 'country_id': False}], 'report_id': 14, 'allow_domestic': True, 'fiscal_position': 'all', 'available_vat_fiscal_positions': [], 'date': {'string': 'From 12/26/2021\nto  12/31/2023', 'period_type': 'custom', 'mode': 'range', 'date_from': '2021-12-26', 'date_to': '2023-12-31', 'filter': 'custom'}, 'available_horizontal_groups': [], 'selected_horizontal_group_id': None, 'account_type': [{'id': 'trade_receivable', 'name': 'Receivable', 'selected': True}, {'id': 'non_trade_receivable', 'name': 'Non Trade Receivable', 'selected': False}, {'id': 'trade_payable', 'name': 'Payable', 'selected': True}, {'id': 'non_trade_payable', 'name': 'Non Trade Payable', 'selected': False}], 'account_display_name': 'Trade Partners', 'all_entries': False, 'buttons': [{'name': 'PDF', 'sequence': 10, 'action': 'export_file', 'action_param': 'export_to_pdf', 'file_export_type': 'PDF'}, {'name': 'XLSX', 'sequence': 20, 'action': 'export_file', 'action_param': 'export_to_xlsx', 'file_export_type': 'XLSX'}, {'name': 'Save', 'sequence': 100, 'action': 'open_report_export_wizard'}], 'partner': True, 'partner_ids': [], 'partner_categories': [], 'selected_partner_ids': [], 'selected_partner_categories': [], 'unreconciled': False, 'search_bar': True, 'unfold_all': False, 'column_headers': [[{'name': 'From 12/26/2021\nto  12/31/2023', 'forced_options': {'date': {'string': 'From 12/26/2021\nto  12/31/2023', 'period_type': 'custom', 'mode': 'range', 'date_from': '2021-12-26', 'date_to': '2023-12-31', 'filter': 'custom'}}}]], 'columns': [{'name': 'JRNL', 'column_group_key': "(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))", 'expression_label': 'journal_code', 'sortable': False, 'figure_type': 'none', 'blank_if_zero': True, 'style': 'text-align: center; white-space: nowrap;'}, {'name': 'Account', 'column_group_key': "(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))", 'expression_label': 'account_code', 'sortable': False, 'figure_type': 'none', 'blank_if_zero': True, 'style': 'text-align: center; white-space: nowrap;'}, {'name': 'Ref', 'column_group_key': "(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))", 'expression_label': 'ref', 'sortable': False, 'figure_type': 'none', 'blank_if_zero': True, 'style': 'text-align: center; white-space: nowrap;'}, {'name': 'Due Date', 'column_group_key': "(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))", 'expression_label': 'date_maturity', 'sortable': False, 'figure_type': 'none', 'blank_if_zero': True, 'style': 'text-align: center; white-space: nowrap;'}, {'name': 'Matching Number', 'column_group_key': "(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))", 'expression_label': 'matching_number', 'sortable': False, 'figure_type': 'none', 'blank_if_zero': True, 'style': 'text-align: center; white-space: nowrap;'}, {'name': 'Debit', 'column_group_key': "(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))", 'expression_label': 'debit', 'sortable': False, 'figure_type': 'monetary', 'blank_if_zero': True, 'style': 'text-align: center; white-space: nowrap;'}, {'name': 'Credit', 'column_group_key': "(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))", 'expression_label': 'credit', 'sortable': False, 'figure_type': 'monetary', 'blank_if_zero': True, 'style': 'text-align: center; white-space: nowrap;'}, {'name': 'Amount Currency', 'column_group_key': "(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))", 'expression_label': 'amount_currency', 'sortable': False, 'figure_type': 'monetary', 'blank_if_zero': True, 'style': 'text-align: center; white-space: nowrap;'}, {'name': 'Balance', 'column_group_key': "(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))", 'expression_label': 'balance', 'sortable': False, 'figure_type': 'monetary', 'blank_if_zero': False, 'style': 'text-align: center; white-space: nowrap;'}, {'name': 'POLICY NO', 'column_group_key': "(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))", 'expression_label': 'policy_no', 'sortable': False, 'figure_type': 'none', 'blank_if_zero': True, 'style': 'text-align: center; white-space: nowrap;'}, {'name': 'ID NO', 'column_group_key': "(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))", 'expression_label': 'id_no', 'sortable': False, 'figure_type': 'none', 'blank_if_zero': True, 'style': 'text-align: center; white-space: nowrap;'}], 'column_groups': {"(('forced_options', (('date', (('date_from', '2021-12-26'), ('date_to', '2023-12-31'), ('filter', 'custom'), ('mode', 'range'), ('period_type', 'custom'), ('string', 'From 12/26/2021\\nto  12/31/2023'))),)), ('horizontal_groupby_element', ()))": {'forced_options': {'date': {'string': 'From 12/26/2021\nto  12/31/2023', 'period_type': 'custom', 'mode': 'range', 'date_from': '2021-12-26', 'date_to': '2023-12-31', 'filter': 'custom'}}, 'forced_domain': []}}, 'show_debug_column': False, 'show_growth_comparison': None, 'order_column': None, 'hierarchy': False, 'display_hierarchy_filter': False, 'forced_domain': ['!', '&', '&', '&', ('credit', '=', 0.0), ('debit', '=', 0.0), ('amount_currency', '!=', 0.0), ('journal_id', 'in', [4])], 'unposted_in_period': True}

        partner_ladger = self.env['account.partner.ledger.report.handler']
        roww += 1
        for rec in partner_ids:
            print("##########################3333")
        query = partner_ladger.sudo()._get_aml_values(options,[])
        if query:
            if query[rec.id]:
                for line in query[rec.id]:
                    col = 5
                    worksheet.write(roww, col, rec.name, multi_record_center)
                    col += 1
                    worksheet.write(roww, col, line["move_name"], multi_record_center)
                    col += 1
                    worksheet.write(roww, col, line["policy_no"], multi_record_center)
                    col += 1
                    worksheet.write(roww, col, line["id_no"], multi_record_center)
                    col += 1
                    worksheet.write(roww, col, line["account_name"], multi_record_center)
                    col += 1
                    worksheet.write(roww, col, line["ref"], multi_record_center)
                    col += 1
                    worksheet.write(roww, col, line["date"].strftime('%m-%d-%Y'), multi_record_center )
                    col += 1
                    worksheet.write(roww, col, line["matching_number"], multi_record_center)
                    col += 1
                    worksheet.write(roww, col, line["debit"], multi_record_center)
                    col += 1
                    worksheet.write(roww, col, line["credit"], multi_record_center)
                    col += 1
                    worksheet.write(roww, col, line["amount_currency"], multi_record_center)
                    col += 1
                    worksheet.write(roww, col, line["balance"], multi_record_center)
                    col += 1
                    roww += 1

        fp = io.BytesIO()
        workbook.save(fp)
        hr_leave_id = self.env['excel.report.purchase'].create({
            'excel_file': base64.encodebytes(fp.getvalue()),
            'file_name': filename
        })
        fp.close()

        return {
            'view_mode': 'form',
            'res_id': hr_leave_id.id,
            'res_model': 'excel.report.purchase',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
