# -*- coding: utf-8 -*-

from odoo import models, fields, api
import numpy as np
import json
import requests
import json
from odoo.exceptions import UserError, ValidationError


class data_migration_module(models.Model):
    _name = 'res.migration.data'
    model_id = fields.Many2one("ir.model")
    fields_id = fields.Many2many("ir.model.fields", "mifrate_fields", "field_id", "id",
                                 domain="[('model_id','=',model_id),('ttype','!=','many2many'),('store','=',True)]")
    from_id = fields.Integer()
    to_id = fields.Integer()
    url = fields.Char()
    company_id = fields.Many2one('res.company')
    is_new = fields.Boolean()
    fields_id_many = fields.Many2one("ir.model.fields", domain="[('model_id','=',model_id),('ttype','=','many2many')]")

    def create_fields(self):
        url = self.url + "/api/add_field"

        payload = json.dumps({
            "jsonrpc": "2.0",
            "params": {
                "model_id": self.model_id.model
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'frontend_lang=en_US; session_id=bf95ce326b66bcd8aa49a406ba4d1c9e16b829f5'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        raise ValidationError(response.text)

    def send_many2many(self):
        url = self.url + "/api/update_data_m2m"
        domain=(self.fields_id_many.name,'!=',False)
        print("=====================",url)
        mod_search = self.env[self.model_id.model].sudo().search([domain])
        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'session_id=bf95ce326b66bcd8aa49a406ba4d1c9e16b829f5'
        }
        for rec in mod_search:
            payload =  ({
                "jsonrpc": "2.0",
                "params": {
                    "model_id": self.model_id.model,
                    "id": rec.id,
                    "field": self.fields_id_many.name,
                    "other_id": rec[self.fields_id_many.name].ids
                }
            })



            response = requests.request("GET", url, headers=headers, data=json.dumps(payload))

            print(response.text)

    def send_data(self):
        url = self.url + "/api/update_data"
        mod_search = self.env[self.model_id.model].search([])
        data = []
        # for rec in mod_search:
        dict = []
        fids_char = 'id,'
        update_fields = ''
        for field in self.fields_id:
            if field.ttype in ('datetime', 'date'):
                # fids_char += "CONVERT(nvarchar(30),%s,10)"%(field.name)+","
                fids_char += "CAST(%s AS varChar(20))" % (field.name) + ","
            else:

                fids_char += field.name + ","
        #     update_fields+=field.name+"=%s"+" and "
        # print(">>>>>>>>>>>>>>.>>>>>>>",update_fields[:-4])

        self.env.cr.execute(
            "SELECT %s FROM %s  where id>=%s and id<=%s" % (fids_char[:-1], self.model_id.model.replace(".", "_") ,self.from_id,self.to_id))
        # self.env.cr.execute(
        #     "SELECT %s FROM %s where active='true'" % (
        #         fids_char[:-1], self.model_id.model.replace(".", "_")))
        data = self.env.cr.dictfetchall()
        print(">>>>>>>>>>..", data)
        payload = json.dumps({
            "jsonrpc": "2.0",
            "params": {
                "model_id": self.model_id.model,
                "data": data,
                "is_new": self.is_new
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'frontend_lang=en_US; session_id=bf95ce326b66bcd8aa49a406ba4d1c9e16b829f5'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)
        raise ValidationError(response.text)

        # for rec in data:
        #     result = rec.items()
        #     data2 = list(result)
        #     numpyArray = np.array(data2)
        #     data_search = self.env[self.model_id.model].search([('id', '=', numpyArray[0][1])])
        #     data_search.write(rec)
