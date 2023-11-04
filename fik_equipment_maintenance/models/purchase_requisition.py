from odoo import models, fields, api, _

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    is_requisition = fields.Boolean("Is Order From Maintenance Requisition?", default=False)
    maintenance_id = fields.Many2one('maintenance.request', 'Maintenance Request')

    @api.model
    def get_requisition_week_data(self):
        cr = self._cr

        query = """
              SELECT pr.ordering_date AS ordering_date,count(*) as count
              FROM purchase_requisition pr 
              group by pr.ordering_date
              order by pr.ordering_date

              """
        cr.execute(query)
        partner_data = cr.dictfetchall()
        data_set = {}
        mydate = []
        mycount = []
        list_value = []
        dict = {}
        count = 0
        days = ["Monday", "Tuesday", "Wednesday", "Thursday",
                "Friday", "Saturday", "Sunday"]
        for data in partner_data:
            print("------------", data)
            if data['ordering_date']:
                mydate = data['ordering_date'].weekday()
                if mydate >= 0:
                    value = days[mydate]
                    list_value.append(value)

                    list_value1 = list(set(list_value))

                    for record in list_value1:
                        count = 0
                        for rec in list_value:
                            if rec == record:
                                count = count + 1
                            dict.update({record: count})
                        keys, values = zip(*dict.items())
                        # dict.update({'record': data['count_data'], 'day': value})
                        data_set.update({"data": dict})
        return data_set

