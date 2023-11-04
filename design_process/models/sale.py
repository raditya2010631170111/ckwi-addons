from odoo import models, fields, api, _
from odoo.exceptions import UserError



class SaleOrderLine(models. Model):
    _inherit = 'sale.order.line'
    _description = 'Sale Order Line'



    sku_id = fields.Many2one("stock.production.lot","SKU No")
    sku = fields.Char("SKU No")
    request_date = fields.Date("Ship Date", copy=False,required=True)
    is_revisi = fields.Boolean('is_revisi', related='order_id.is_revisi')
    finish_id = fields.Many2one("design.finish","Finish")
    no_mo = fields.Char("No. MO", default="New", readonly=True, copy=False)
    no_po = fields.Char("No PO")
    no_po_cust = fields.Char("Cust Ref", store=True)
    list_mo = fields.Char("List MO", compute="get_mo_list", store=True, copy=False)
    cont_load = fields.Char("Cont. Load", 
    default="Combine Cont'"
    )
    # cust_ref = fields.Char('Cust Reference', related='order_id.origin', store=True, readonly=False )

    @api.onchange('is_revisi')
    def _onchange_is_revisi(self):
        for line in self:
            if not line.is_revisi:
                line.request_date = False

    @api.depends("no_mo")
    def get_mo_list(self):
        for line in self:
            line.list_mo = line.no_mo[:6]
            
class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
   
    def get_contact_reviews(self):
        for x in self:
            sj = self.env['sale.order'].search([('name','=', x.name)])
            order_line = []
            for line in sj.order_line:
                order_line.append({
                    'product_id': line.product_id.name,
                    'name': line.name,
                    # 'sku_id': line.sku_id.name,
                    'sku': line.sku,
                    'no_mo': line.no_mo,
                    'no_po': line.no_po,
                    'cust_ref': line.cust_ref,
                    'no_po_cust' : line.no_po_cust,
                    'cont_load': line.cont_load,
                    'product_uom_qty': line.product_uom_qty,
                    'request_date': line.request_date,
                    'fabric_colour_id': line.fabric_colour_id.name,
                    # 'material_finishing': line.material_finishing,
                    'material_finish_id': line.material_finish_id.name,
                    'finish_id': line.finish_id.name,
                    'name_item' : line.name_item,
                    'product_uom' : line.product_uom.name,
                    })
            return order_line
    