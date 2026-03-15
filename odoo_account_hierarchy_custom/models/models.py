# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MoveLine(models.Model):
    _inherit = "account.move.line"

    # @api.onchange('account_id')
    # def _onchange_levels(self):
    #     return {'domain': {'account_id': [('level', 'in', level.ids), ('is_view', '=', True)]}}


class account(models.Model):
    _inherit = "account.account"
    level = fields.Many2one("account.level", string="Level")

    parent_level = fields.Many2one("account.level", related="parent_id.level", store=True, string="Parent Level")
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    level_ids = fields.Many2many("account.level", string="Allow Levels", compute='get_level_ids')
    parent_id = fields.Many2one('account.account', string='Parent Name', domain="[('is_view','=',True),('level','in',level_ids)]")
    is_view = fields.Boolean("Is Parent")
    @api.depends('level')
    def get_level_ids(self):
        for rec in self:
            level_ids = self.env['account.level'].search([('name', '<', rec.level.name)],order='name desc',limit=1)

            rec.level_ids=[]
            if level_ids:

                rec.level_ids=[(4,index.id)for index in level_ids]



    @api.onchange('level', 'parent_id', 'name', 'account_type')
    def _onchange_levels(self):
        for rec in self:
            if rec.parent_id:
                account_id = self.env['account.account'].search(
                    [('parent_id', '=', rec.parent_id.id)])

                index = 1
                if rec.level:
                    index = rec.level.prefix
                if rec.parent_id.level:
                    index = rec.level.prefix
                if  index!=0:
                    if account_id:
                        rec.code = str(
                            rec.company_id.prefix_char) if rec.company_id.prefix_char else '' + rec.parent_id.code + str(
                            len(account_id) + 1).zfill(index)
                    else:
                        rec.code = str(
                            rec.company_id.prefix_char) if rec.company_id.prefix_char else '' + rec.parent_id.code + str(
                            1).zfill(index)

        # if self.level:
        #     level = self.env['account.level'].search([('name','<',self.level.name)])
        #
        #     # return {'domain':{'parent_id':[('level','in',level.ids),('is_view','=',True)]}}
        #     return {'domain':{'parent_id':[('level','in',level.ids),('is_view','=',True)]}}
        # else:
        #     return {'domain': {'parent_id': []}}

    @api.model
    def create(self, vals):
        res = super(account, self).create(vals)
        if res.parent_id:
            account_id = self.env['account.account'].search(
                [('parent_id', '=', res.parent_id.id), ('id', '!=', res.id)])
            index = 1
            if res.level:
                index = res.level.prefix
            if res.parent_id.level:
                index = res.level.prefix
            if index != 0:
                if account_id:
                    res.code = str(
                        res.company_id.prefix_char) if res.company_id.prefix_char else '' + res.parent_id.code + str(
                        len(account_id) + 1).zfill(index)
                else:
                    res.code = str(
                        res.company_id.prefix_char) if res.company_id.prefix_char else '' + res.parent_id.code + str(
                        1).zfill(index)

        return res

    def write(self, vals):
        res = super(account, self).write(vals)
        if 'parent_id' in vals:
            for rec in self:

                if rec.parent_id:
                    account_id = rec.env['account.account'].search(
                        [('parent_id', '=', rec.parent_id.id), ('id', '!=', rec.id)])
                    index = 0
                    if rec.parent_id.level and rec.level:
                        index = rec.level.prefix
                    if index!=0:
                        if account_id:
                            rec.code = str(
                                rec.company_id.prefix_char) if rec.company_id.prefix_char else '' + rec.parent_id.code + str(
                                len(account_id) + 1).zfill(index)
                        else:
                            rec.code = str(rec.company_id.prefix_char) if rec.company_id.prefix_char else ''  + rec.parent_id.code + str(1).zfill(index)

        return res
