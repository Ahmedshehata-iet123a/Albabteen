import json

from odoo import http
from odoo.http import request
import datetime
import numpy as np


class Move(http.Controller):

    @http.route('/api/update_data_m2m', type="json", auth="public")
    def update_records_datam2m(self, **kwargs):

        data_search = request.env[kwargs['model_id']].sudo().search([('id', '=', kwargs['id'])])
        print(">>>>>>>>>>>>>>>>>>>>>", kwargs['other_id'])

        if data_search:
            data_search.sudo().write({kwargs['field']: [(4, line) for line in kwargs['other_id']]})

        return {"status": "success", "massage": "update"}

    @http.route('/api/update_data', type="json", auth="public")
    def update_records_data(self, **kwargs):

        for rec in kwargs['data']:
            result = rec.items()
            data2 = list(result)
            numpyArray = np.array(data2)
            print("=================", rec)
            data_search = request.env[kwargs['model_id']].sudo().search([('id', '=', numpyArray[0][1])])
            if data_search:
                if kwargs['model_id']=='stock.move':
                    if 'analytic_account_id' in rec:
                        print("=================",{rec['analytic_account_id']:100})

                        data_search.write({
                      'analytic_distribution':{rec['analytic_account_id']:100}
                        })
                else:
                      data_search.write(rec)
                # data_search.write({'x_is_migrate': True})
                print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..", rec)
            else:
                if kwargs['is_new'] == True:
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..", rec)
                    new = request.env[kwargs['model_id']].sudo().create(rec)
                    request.env.cr.execute("""update %s set id =%s  where id =%s""" %(kwargs['model_id'].replace(".", "_"),
                            numpyArray[0][1],new.id )
                       )

                    # return {"status": "success",
                    #         "massage": """update %s set id =%s where id =%s""" %(kwargs['model_id'].replace(".", "_"),
                    #         numpyArray[0][1],new.id )}

        return {"status": "success", "massage": "update"}

    @http.route('/api/add_field', type="json", auth="public")
    def add_field_records_data(self, **kwargs):
            print("==========================")
            model_id = request.env['ir.model'].sudo().search([('model', '=', kwargs['model_id'])])
            field = request.env['ir.model.fields'].sudo().search(
                [('model_id', '=', model_id.id), ('ttype', '=', 'boolean'), ('name', '=', 'x_is_migrate')])
            if not field:
                data = request.env['ir.model.fields'].sudo().create({
                    'name': 'x_is_migrate',
                    'field_description': 'x_is_migrate',
                    'model_id': model_id.id,
                    'ttype': 'boolean'
                })
                return {"status": "success", "massage": "is create %s" % (data)}
