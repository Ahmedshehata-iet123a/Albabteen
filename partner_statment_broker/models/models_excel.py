from odoo import fields, models, api,_

from odoo import _, fields, models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import FORMATS


class OutstandingStatementXslx(models.AbstractModel):
    _inherit = "report.p_s.report_outstanding_statement_xlsx"

    def _write_currency_lines(self, row_pos, sheet, partner, currency, data):
        partner_data = data.get("data", {}).get(partner.id, {})
        currency_data = partner_data.get("currencies", {}).get(currency.id)
        account_type = data.get("account_type", False)
        row_pos += 2
        statement_header = _("%(payable)sStatement up to %(end)s in %(currency)s") % {
            "payable": account_type == "payable" and _("Supplier ") or "",
            "end": partner_data.get("end"),
            "currency": currency.display_name,
        }

        sheet.merge_range(
            row_pos, 0, row_pos, 6, statement_header, FORMATS["format_right_bold"]
        )
        row_pos += 1
        sheet.write(
            row_pos, 0, _("Reference Number"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(row_pos, 1, _("Date"), FORMATS["format_theader_yellow_center"])
        sheet.write(row_pos, 2, _("Due Date"), FORMATS["format_theader_yellow_center"])
        sheet.write(
            row_pos, 3, _("Description"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(
            row_pos, 4, _("POLICY NO"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(
            row_pos, 5, _("ID NO"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(row_pos, 6, _("Original"), FORMATS["format_theader_yellow_center"])
        sheet.write(
            row_pos, 7, _("Open Amount"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(row_pos, 8, _("Balance"), FORMATS["format_theader_yellow_center"])
        for line in currency_data.get("lines"):
            row_pos += 1
            name_to_show = (
                                   line.get("name", "") == "/" or not line.get("name", "")
                           ) and line.get("ref", "")
            if line.get("name", "") != "/":
                if not line.get("ref", ""):
                    name_to_show = line.get("name", "")
                else:
                    if (line.get("ref", "") in line.get("name", "")) or (
                            line.get("name", "") == line.get("ref", "")
                    ):
                        name_to_show = line.get("name", "")
                    else:
                        name_to_show = line.get("ref", "")
            sheet.write(
                row_pos, 0, line.get("move_id", ""), FORMATS["format_tcell_left"]
            )
            sheet.write(
                row_pos, 1, line.get("date", ""), FORMATS["format_tcell_date_left"]
            )
            sheet.write(
                row_pos,
                2,
                line.get("date_maturity", ""),
                FORMATS["format_tcell_date_left"],
            )
            sheet.write(row_pos, 3, name_to_show, FORMATS["format_distributed"])
            sheet.write(row_pos, 4, line.get("policy_no", ""), FORMATS["format_distributed"])
            sheet.write(row_pos, 5, line.get("id_no", ""), FORMATS["format_distributed"])
            sheet.write(
                row_pos, 6, line.get("amount", ""), FORMATS["current_money_format"]
            )
            sheet.write(
                row_pos, 7, line.get("open_amount", ""), FORMATS["current_money_format"]
            )
            sheet.write(
                row_pos, 8, line.get("balance", ""), FORMATS["current_money_format"]
            )
        row_pos += 1
        sheet.write(
            row_pos, 1, partner_data.get("end"), FORMATS["format_tcell_date_left"]
        )
        sheet.merge_range(
            row_pos, 2, row_pos, 4, _("Ending Balance"), FORMATS["format_tcell_left"]
        )
        sheet.write(
            row_pos, 6, currency_data.get("amount_due"), FORMATS["current_money_format"]
        )
        return row_pos
# class ActivityStatementXslx(models.AbstractModel):
#     _inherit = "report.p_s.report_activity_statement_xlsx"
#     def _write_currency_lines(self, row_pos, sheet, partner, currency, data):
#         partner_data = data.get("data", {}).get(partner.id, {})
#         currency_data = partner_data.get("currencies", {}).get(currency.id)
#         account_type = data.get("account_type", False)
#         row_pos += 2
#         statement_header = _(
#             "%(payable)sStatement between %(start)s and %(end)s in %(currency)s"
#         ) % {
#             "payable": account_type == "payable" and _("Supplier ") or "",
#             "start": partner_data.get("start"),
#             "end": partner_data.get("end"),
#             "currency": currency.display_name,
#         }
#
#         sheet.merge_range(
#             row_pos, 0, row_pos, 6, statement_header, FORMATS["format_right_bold"]
#         )
#         row_pos += 1
#         sheet.write(
#             row_pos, 0, _("Reference Number"), FORMATS["format_theader_yellow_center"]
#         )
#         sheet.write(row_pos, 1, _("Date"), FORMATS["format_theader_yellow_center"])
#         sheet.write(row_pos, 2, _("POLICY NO"), FORMATS["format_theader_yellow_center"])
#         sheet.write(row_pos, 3, _("ID NO"), FORMATS["format_theader_yellow_center"])
#         sheet.merge_range(
#             row_pos,
#             4,
#             row_pos,
#             6,
#             _("Description"),
#             FORMATS["format_theader_yellow_center"],
#         )
#         sheet.write(
#             row_pos, 7, _("Open Amount"), FORMATS["format_theader_yellow_center"]
#         )
#         sheet.write(row_pos, 8, _("Balance"), FORMATS["format_theader_yellow_center"])
#         row_pos += 1
#         sheet.write(
#             row_pos, 1, partner_data.get("start"), FORMATS["format_tcell_date_left"]
#         )
#         sheet.merge_range(
#             row_pos, 2, row_pos, 4, _("Balance Forward"), FORMATS["format_tcell_left"]
#         )
#         sheet.write(
#             row_pos,
#             6,
#             currency_data.get("balance_forward"),
#             FORMATS["current_money_format"],
#         )
#         for line in currency_data.get("lines"):
#             row_pos += 1
#             name_to_show = (
#                 line.get("name", "") == "/" or not line.get("name", "")
#             ) and line.get("ref", "")
#             if line.get("name", "") != "/":
#                 if not line.get("ref", ""):
#                     name_to_show = line.get("name", "")
#                 else:
#                     if (line.get("name", "") in line.get("ref", "")) or (
#                         line.get("name", "") == line.get("ref", "")
#                     ):
#                         name_to_show = line.get("name", "")
#                     elif line.get("ref", "") not in line.get("name", ""):
#                         name_to_show = line.get("ref", "")
#             sheet.write(
#                 row_pos, 0, line.get("move_id", ""), FORMATS["format_tcell_left"]
#             )
#             sheet.write(
#                 row_pos, 1, line.get("date", ""), FORMATS["format_tcell_date_left"]
#             )
#             sheet.merge_range(
#                 row_pos, 2, row_pos, 4, name_to_show, FORMATS["format_distributed"]
#             )
#             sheet.write(
#                 row_pos, 5, line.get("amount", ""), FORMATS["current_money_format"]
#             )
#             sheet.write(
#                 row_pos, 6, line.get("balance", ""), FORMATS["current_money_format"]
#             )
#         row_pos += 1
#         sheet.write(
#             row_pos, 1, partner_data.get("end"), FORMATS["format_tcell_date_left"]
#         )
#         sheet.merge_range(
#             row_pos, 2, row_pos, 4, _("Ending Balance"), FORMATS["format_tcell_left"]
#         )
#         sheet.write(
#             row_pos, 6, currency_data.get("amount_due"), FORMATS["current_money_format"]
#         )
#         return row_pos
