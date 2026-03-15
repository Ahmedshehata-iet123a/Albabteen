from odoo import fields, models, api,_


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    filter_account_id = fields.Boolean(
        string="Analytic Filter",
        compute=lambda x: x._compute_report_option_filter('filter_account_id'), readonly=False, store=True, depends=['root_report_id'],
    )
    def _init_options_account_id(self, options, previous_options=None):

        # print("=================",previous_options)
        options['account_id'] = [
            {'id': c.id, 'name': c.name} for c in self.env['account.account'].search([])
        ]
        # print("==================================",options)

    @api.model
    def _get_options_account_id_domain(self, options):
        ''' Get select account type in the filter widget (see filter_account_type).
        :param options: The report options.
        :return:        Selected account types.
        '''

        all_account_types = []
        print_lines = []
        for account_type_option in options.get('account_id', []):
            if account_type_option['selected'] :
                print_lines.append(account_type_option)

        return print_lines
    def _init_options_account_type(self, options, previous_options=None):
        '''
        Initialize a filter based on the account_type of the line (trade/non trade, payable/receivable).
        Selects a name to display according to the selections.
        The group display name is selected according to the display name of the options selected.
        '''
        if not self.filter_account_type:
            return

        options['account_type'] = [
            {'id': 'trade_receivable', 'name': _("Receivable"), 'selected': True},
            {'id': 'non_trade_receivable', 'name': _("Non Trade Receivable"), 'selected': False},
            {'id': 'trade_payable', 'name': _("Payable"), 'selected': True},
            {'id': 'non_trade_payable', 'name': _("Non Trade Payable"), 'selected': False},
        ]

        if previous_options and previous_options.get('account_type'):
            print(">>>>>>>>>>>>>>>>>>>>>...",previous_options.get('account_type'))
            previously_selected_ids = {x['id'] for x in previous_options['account_type'] if x.get('selected')}
            for opt in options['account_type']:
                opt['selected'] = opt['id'] in previously_selected_ids

        selected_options = {x['id']: x['name'] for x in options['account_type'] if x['selected']}
        selected_ids = set(selected_options.keys())
        display_names = []

        def check_if_name_applicable(ids_to_match, string_if_match):
            '''
            If the ids selected are part of a possible grouping,
                - append the name of the grouping to display_names
                - Remove the concerned ids
            ids_to_match : the ids forming a group
            string_if_match : the group's name
            '''
            if len(selected_ids) == 0:
                return
            if ids_to_match.issubset(selected_ids):
                display_names.append(string_if_match)
                for selected_id in ids_to_match:
                    selected_ids.remove(selected_id)

        check_if_name_applicable({'trade_receivable', 'trade_payable', 'non_trade_receivable', 'non_trade_payable'}, _("All receivable/payable"))
        check_if_name_applicable({'trade_receivable', 'non_trade_receivable'}, _("All Receivable"))
        check_if_name_applicable({'trade_payable', 'non_trade_payable'}, _("All Payable"))
        check_if_name_applicable({'trade_receivable', 'trade_payable'}, _("Trade Partners"))
        check_if_name_applicable({'non_trade_receivable', 'non_trade_payable'}, _("Non Trade Partners"))
        for sel in selected_ids:
            display_names.append(selected_options.get(sel))
        options['account_display_name'] = ', '.join(display_names)
