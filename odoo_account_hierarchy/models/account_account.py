from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def get_account_hierarchy_lines(self, domain=None):
        debit = 0.0
        credit = 0.0
        balance = 0.0
        domain = []
        ctx = dict(self._context or {})
        account_account_env = self.env['account.account']
        account_move_line_env = self.env['account.move.line']
        for rec in self:
            child_of_ids = account_account_env.search([('id', 'child_of', [rec.id])]).ids
            domain_sql = ""
            if ctx['state'] == 'posted':
                domain_sql += "where mv.state='posted'"
                domain += [('move_id.state', '=', 'posted')]
            else:
                domain_sql += "where mv.state in('posted','draft')"
                domain += [('move_id.state', 'in', ['draft', 'posted'])]

            if child_of_ids:
                child_domain = '('
                for child in child_of_ids:
                    child_domain += str(child) + ","
                child_domain = child_domain[:-1] + ")"

                domain_sql += "and line.account_id in %s" % (child_domain)
                domain.append(('account_id', 'in', child_of_ids))
            if ctx['date_from'] != 'False':
                domain_sql += "and line.date >= %s" % (ctx['date_from'])
                domain.append(('date', '>=', ctx['date_from']))
            if ctx['date_to'] != 'False':
                domain_sql += "and line.date <= %s" % (ctx['date_from'])
                domain.append(('date', '<=', ctx['date_to']))
            print("==========================", domain_sql)
            self.env.cr.execute(
                """ select sum(line.debit)as debit,sum(line.credit)as credit ,sum(line.debit-line.credit)as balance
                from account_move_line as line inner join  account_move as mv on mv.id=line.move_id %s 
                """ %(domain_sql))
            result=self.env.cr.fetchall()
            print(">>>",result[0][0],type(result[0][0]))
            print(">>>",result[0][1])
            print(">>>",result[0][2])

            # # for move_line in account_move_line_env.search(domain):
            if result:

                balance+= result[0][2] if result[0][2] else 0
                credit+= result[0][1] if result[0][1] else 0
                debit+= result[0][0] if result[0][0] else 0
            rec.balance = balance
            rec.credit = credit
            rec.debit = debit
        return debit, credit, balance

    move_line_ids = fields.One2many('account.move.line', 'account_id', string='Journal Items', copy=False)
    debit = fields.Float(compute="_compute_account_account_values", digits=dp.get_precision('Account'), string='Debit')
    credit = fields.Float(compute="_compute_account_account_values", digits=dp.get_precision('Account'),
                          string='Credit')
    balance = fields.Float(compute="_compute_account_account_values", digits=dp.get_precision('Account'),
                           string='Balance')
    is_view = fields.Boolean()
    parent_id = fields.Many2one('account.account', string='Parent Name',domain="[('is_view','=',True)]")
    child_ids = fields.One2many('account.account', 'parent_id', string='Children')
    has_child = fields.Boolean(string="Has Child", compute='_compute_account_has_child')

    @api.depends('move_line_ids', 'move_line_ids.amount_currency', 'move_line_ids.debit', 'move_line_ids.credit')
    def _compute_account_account_values(self):
        debit = 0.0
        credit = 0.0
        balance = 0.0
        account_account_env = self.env['account.account']
        account_move_line_env = self.env['account.move.line']
        domain = [('move_id.state', '=', 'posted')]
        for rec in self:
            child_of_ids = account_account_env.search([('id', 'child_of', [rec.id])]).ids
            domain.append(('account_id', 'in', child_of_ids))
            for move_line in account_move_line_env.search(domain):
                balance += move_line.debit - move_line.credit
                credit += move_line.credit
                debit += move_line.debit
            rec.balance = balance
            rec.credit = credit
            rec.debit = debit

    @api.depends('child_ids')
    def _compute_account_has_child(self):
        for rec in self:
            if len(rec.child_ids) >= 1:
                rec.has_child = True
            else:
                rec.has_child = False
