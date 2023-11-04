from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResLoad(models.Model):
    _name = 'res.load'
    _description = 'Res Load'

    name = fields.Char(string="Value", )
    proportion = fields.Integer(string='Value Proportion')

    @api.model
    def create(self, vals):
        if 'name' in vals and 'proportion' not in vals:
            vals['proportion'] = vals['name']
        return super(ResLoad, self).create(vals)

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            # Lakukan penghitungan nilai proportion berdasarkan nilai name
            self.proportion = self.name

# class SaleOrder(models.Model):
#     _inherit = 'sale.order'

#     partner_id = fields.Many2one(
#         'res.partner', string='Customer', readonly=True,
#         states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
#         required=True, change_default=True, index=True, tracking=1,
#         domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
#     partner_invoice_id = fields.Many2one(
#         'res.partner', string='Invoice Address',
#         readonly=True, required=True,
#         states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
#         domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
#     partner_shipping_id = fields.Many2one(
#         'res.partner', string='Delivery Address', readonly=True, required=True,
#         states={'draft': [('readonly', False)], 'sent': [('readonly', False)], 'sale': [('readonly', False)]},
#         domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)

#     pricelist_id = fields.Many2one(
#         'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
#         required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
#         domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
#         help="If you change the pricelist, only newly added lines will be affected.")

class SummaryCosting(models.Model):
    _name = 'summary.costing'
    _description = 'Summary Costing'
    _rec_name = 'item_id'
    

    item_id = fields.Many2one('product.product', 'Item No')
    item_no = fields.Char('Item No')
    item_description = fields.Char('Item Description')
    name = fields.Char('Material')
    request_no = fields.Char("No. Spec Design",readonly=True, copy=False)
    crm_id = fields.Many2one("crm.lead","Oportunity", readonly=True)
    rnd_id = fields.Many2one("design.process","RnD", readonly=True)
    net_cubic_cost = fields.Float('Net Cubic (M3)',compute='_compute_cubic',digits=(12,5))
    unit_wood_cost = fields.Float('Unit Wood Cost',compute='_compute_unit_wood')
    unit_labour_cost = fields.Float('Unit Labour Cost',compute='_compute_unit_labour',digits=(12,2))
    total_wood_cost = fields.Float('Total',compute='_compute_total_wood')
    net_cubic_change = fields.Float('Net Cubic (M3)',compute='_compute_cubic')
    unit_wood_change = fields.Float('Unit Wood Cost',compute='_compute_unit_wood')
    unit_labour_change = fields.Float('Unit Labour Cost',compute='_compute_unit_labour')
    total_wood_change = fields.Float('Total',compute='_compute_total_wood')
    currency = fields.Selection([
        ('RP', 'RP'),
        ('NT', 'NT'),
        ('RMB', 'RMB'),
        ('USA', 'USA'),
    ], string='Currency',default='RP')
    res_load_id = fields.Many2one('res.load',string='Proportion')
    proportion = fields.Integer(string='value Proportion', compute="compute_proportion")
    detail_material_ids = fields.Many2many('design.material', string="Material")
    detail_finish_ids = fields.Many2many('design.finish', string="Finish")

    
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], readonly=True, default='draft',required=True)
    
    def action_confirm(self):
        self.write({'state': 'confirm'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})
    
    def action_reset(self):
        self.write({'state': 'draft'})

    # @api.constrains('state')
    # def _check_state(self):
    #     for record in self:
    #         if record.state == 'done' and record.id:
    #             raise ValidationError('You cannot edit a record that is done!')
   
    # @api.multi
    
        # for material in self.detail_material_ids:
        #     for finish in self.detail_finish_ids:
    def action_sale_quotations_new(self):
        line_detail_vals = []
        # for material_id in self.detail_material_ids:
            # for finish_id in self.detail_finish_ids:
        line_detail_vals.append((0, 0, {
                    'product_id': self.item_id.id,
                    'material_finish_id': self.detail_material_ids.ids,
                    'finish_id': self.detail_finish_ids.ids,
                    'william_fob_price': self.net_profit,
                    # set any other required fields here
                }))

        sale_order = self.env['sale.order'].create({
            'order_line': line_detail_vals,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'New Sale Quotation',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }


    @api.depends('res_load_id.proportion')
    def compute_proportion(self):
        for record in self:
            record.proportion = record.res_load_id.proportion
    
    @api.depends('wood_costing_line_ids','product_cost')
    def _compute_cubic(self):
        for rec in self:
            rec.net_cubic_cost = sum([x.net_cubic for x in rec.wood_costing_line_ids])
            res = 0.00
            if rec.product_cost > 0:
                res = round(rec.net_cubic_cost / rec.product_cost * 100,2)
            rec.net_cubic_change = res
    
    @api.depends('wood_costing_line_ids','product_cost')
    def _compute_unit_wood(self):
        for rec in self:
            rec.unit_wood_cost = sum([x.component_price for x in rec.wood_costing_line_ids])
            res = 0.00
            if rec.product_cost > 0:
                res = round(rec.unit_wood_cost / rec.product_cost * 100,2)
            rec.unit_wood_change = res

    @api.depends('net_cubic_cost','rp_exchange_rate','product_cost')
    def _compute_unit_labour(self):
        for rec in self:
            cost = 0.00
            if rec.rp_exchange_rate :
                cost = round((rec.net_cubic_cost*(1800000+350000)+2.30921*17500) / rec.rp_exchange_rate,2)
            rec.unit_labour_cost = cost
            res = 0.00
            if rec.product_cost > 0:
                res = round(rec.unit_labour_cost / rec.product_cost * 100,2)
            rec.unit_labour_change = res

    @api.depends('net_cubic_cost','unit_wood_cost','unit_labour_cost','product_cost')
    def _compute_total_wood(self):
        for rec in self:
            rec.total_wood_cost = rec.net_cubic_cost + rec.unit_wood_cost + rec.unit_labour_cost
            res = 0.00
            if rec.product_cost > 0:
                res = round(rec.total_wood_cost / rec.product_cost * 100,2)
            rec.total_wood_change = res

    oil_paint_cost = fields.Float('Oil & Paint',compute='_compute_oil_paint_cost')
    hardware_cost = fields.Float('Hardware',compute='_compute_hardware_cost')
    special_hardware_cost = fields.Float('Special Hardware')
    canvas_cost = fields.Float('Canvas',compute='_compute_canvas_cost')
    packing_cost = fields.Float('Packing',compute='_compute_packing_cost')
    total_other_material_cost = fields.Float('Total',compute='_compute_total_other_material_cost')
    oil_paint_change = fields.Float('Oil & Paint',compute='_compute_oil_paint_cost')
    hardware_change = fields.Float('Hardware',compute='_compute_hardware_cost')
    special_hardware_change = fields.Float('Special Hardware',compute='_compute_special_hardware_change')
    canvas_change = fields.Float('Canvas',compute='_compute_canvas_cost')
    packing_change = fields.Float('Packing',compute='_compute_packing_cost')
    total_other_material_change = fields.Float('Total',compute='_compute_total_other_material_cost')
    value_real_hardware = fields.Float(string='Real',
        compute='_compute_real' )
    real_hardware_cost = fields.Float(string='Reals')
    
    @api.depends('hadware_costing_line_ids')
    def _compute_real(self):
        for rec in self:
            rec.value_real_hardware = sum([x.cost for x in rec.hadware_costing_line_ids])

    @api.onchange('currency')
    def _onchange_currency(self):
        for rec in self:
            rec.value_real_hardware = sum([x.cost for x in rec.hadware_costing_line_ids])
            if rec.currency == 'RP':
                rec.real_hardware_cost = rec.value_real_hardware
            elif rec.currency == 'NT':
                rec.real_hardware_cost = rec.value_real_hardware * rec.nt_exchange_rate
            elif rec.currency == 'RMB':
                rec.real_hardware_cost = rec.value_real_hardware * rec.rmb_exchange_rate
            elif rec.currency == 'USA':
                rec.real_hardware_cost = rec.value_real_hardware * rec.usa_exchange_rate
            
    @api.depends('net_cubic_cost','product_cost')
    def _compute_oil_paint_cost(self):
        for rec in self:
            rec.oil_paint_cost = round(rec.net_cubic_cost * 320,2)
        res = 0.00
        if rec.product_cost > 0:
            res = round(rec.oil_paint_cost / rec.product_cost * 100,2)
        rec.oil_paint_change = res

    @api.depends('hadware_costing_line_ids','product_cost','real_hardware_cost')
    def _compute_hardware_cost(self):
        for rec in self:
            total_hardware_cost = rec.real_hardware_cost
            #ini tambah kondisi

            rec.hardware_cost = total_hardware_cost - rec.special_hardware_cost
            res = 0.00
            if rec.product_cost > 0:
                res = round(rec.hardware_cost / rec.product_cost * 100,2)
            rec.hardware_change = res
    
    @api.depends('hardware_cost','product_cost')
    def _compute_special_hardware_change(self):
        for rec  in self:
            res = 0.00
            if rec.product_cost > 0:
                res = round(rec.special_hardware_cost / rec.product_cost * 100,2)
            rec.special_hardware_change = res

    @api.depends('canvas_costing_line_ids','product_cost')
    def _compute_canvas_cost(self):
        for rec in self:
            rec.canvas_cost = sum([x.cost for x in rec.canvas_costing_line_ids])
            res = 0.00
            if rec.product_cost > 0:
                res = round(rec.canvas_cost / rec.product_cost * 100,2)
            rec.canvas_change = res
    
    @api.depends('packing_costing_line_ids','product_cost')
    def _compute_packing_cost(self):
        for rec in self:
            rec.packing_cost = sum([x.cost for x in rec.packing_costing_line_ids])
            #ini tambah kondisi
            res = 0.00
            if rec.product_cost > 0:
                res = round(rec.packing_cost / rec.product_cost * 100,2)
            rec.packing_change = res

    @api.depends('oil_paint_cost','hardware_cost','special_hardware_cost','canvas_cost','packing_cost','product_cost')
    def _compute_total_other_material_cost(self):
        for rec in self:
            rec.total_other_material_cost = rec.oil_paint_cost + rec.hardware_cost + rec.special_hardware_cost + rec.canvas_cost + rec.packing_cost 
            res = 0.00
            if rec.product_cost > 0:
                res = round(rec.total_other_material_cost / rec.product_cost * 100,2)
            rec.total_other_material_change = res

    wood_cost = fields.Float('Wood*15%',compute='_compute_wood_cost')
    hd_cost = fields.Float('H,D.*35%',compute='_compute_hd_cost')
    canvas_cost_15 = fields.Float('Canvas*15%',compute='_compute_canvas_cost_15')
    load = fields.Float('Load 40 Max')
    load_cost = fields.Float('Proportion/Load',compute='_compute_load_cost')
    total_overhead_cost = fields.Float('Total',compute='_compute_total_overhead_cost')
    wood_change = fields.Float('Wood*15%')
    hd_change = fields.Float('H,D.*35%')
    canvas_change_15 = fields.Float('Canvas*15%')
    load_change = fields.Float('$550/Load')
    total_overhead_change = fields.Float('Total',compute='_compute_total_overhead_cost')

    @api.depends('total_wood_cost')
    def _compute_wood_cost(self):
        for rec in self:
            rec.wood_cost = round(rec.total_wood_cost * 15 / 100,2)
    
    @api.depends('total_other_material_cost','special_hardware_cost','canvas_cost')
    def _compute_hd_cost(self):
        for rec in self:
            rec.hd_cost = round((rec.total_other_material_cost - rec.special_hardware_cost - rec.canvas_cost) * 35 / 100,2)

    @api.depends('special_hardware_cost','canvas_cost')
    def _compute_canvas_cost_15(self):
        for rec in self:
            rec.canvas_cost_15 = round((rec.special_hardware_cost + rec.canvas_cost) * 15 / 100,2)
    
    @api.depends('load', 'proportion')
    def _compute_load_cost(self):
        for rec in self:
            res = 0.00
            if rec.load > 0 :
                res = round(rec.proportion/rec.load,2)
            rec.load_cost = res

    @api.depends('wood_cost','hd_cost','canvas_cost_15','load_cost','product_cost')
    def _compute_total_overhead_cost(self):
        for rec in self:
            rec.total_overhead_cost = rec.wood_cost + rec.hd_cost + rec.canvas_cost_15 + rec.load_cost
            res = 0.00
            if rec.product_cost > 0:
                res = round(rec.total_overhead_cost / rec.product_cost * 100,2)
            rec.total_overhead_change = res

    usa_exchange_rate = fields.Float('USA Rate')
    rp_exchange_rate = fields.Float('Rp Rate', default='1.00')
    nt_exchange_rate = fields.Float('NT Rate')
    rmb_exchange_rate = fields.Float('RMB Rate')

    product_cost = fields.Float('Product Cost',compute='_compute_product_cost',store=True)
    product_change = fields.Float('Product Cost',compute='_compute_product_cost')

    @api.depends('total_wood_cost','total_other_material_cost','total_overhead_cost')
    def _compute_product_cost(self):
        for rec in self:
            rec.product_cost = rec.total_wood_cost + rec.total_other_material_cost + rec.total_overhead_cost
            res = 0.00
            if rec.product_cost > 0:
                res = round(rec.product_cost / rec.product_cost * 100,2)
            rec.product_change = res

    selling_price = fields.Float('Selling Price')
    commision_percent = fields.Float('Commision %')
    commision = fields.Float('Commision',compute='_compute_commision')
    net_profit = fields.Float('Net Profit',compute='_compute_net_profit')
    net_profit_percent = fields.Float('Net Profit (%)',compute='_compute_net_profit')

    @api.depends('commision_percent','selling_price')
    def _compute_commision(self):
        for rec in self:
            rec.commision = round(rec.selling_price * rec.commision_percent / 100,2)

    @api.depends('selling_price','product_cost','commision')
    def _compute_net_profit(self):
        for rec in self:
            rec.net_profit = round(rec.selling_price - rec.product_cost - rec.commision,2)
            res = 0.00
            if rec.selling_price > 0:
                res = round(rec.net_profit / rec.selling_price * 100,2)
            rec.net_profit_percent = res

    actual_costing_line_ids = fields.One2many('actual.costing.line', 'summary_costing_id', string='Actual Costing Line')
    wood_costing_line_ids = fields.One2many('wood.costing.line', 'summary_costing_id', string='Wood Costing Line')
    hadware_costing_line_ids = fields.One2many('hardware.costing.line', 'summary_costing_id', string='Hardware Costing Line')
    spesials_material_costing_line_ids = fields.One2many('spesials.material.costing.line', 'summary_costing_id', string='Spesials Material Costing Line')
    canvas_costing_line_ids = fields.One2many('canvas.costing.line', 'summary_costing_id', string='Canvas Costing Line')
    packing_costing_line_ids = fields.One2many('packing.costing.line', 'summary_costing_id', string='Packing Costing Line')

    approved_user_id = fields.Many2one('res.users', string='Approved By')
    assessed_user_id = fields.Many2one('res.users', string='Assessed By')
    calculated_user_id = fields.Many2one('res.users', string='Calculated By')

class ActualCostingLine(models.Model):
    _name = 'actual.costing.line'
    _description = 'Actual Costing Line'

    
    
    summary_costing_id = fields.Many2one('summary.costing', string='Summary Costing')
    product_id = fields.Many2one('product.product', 'Componen')
    net_cubic_cost = fields.Float('Net Cubic (M3)',digits=(12,5))
    unit_wood_cost = fields.Float('Unit Wood Cost')
    unit_labour_cost = fields.Float('Unit Labour Cost',digits=(12,2))
    total_wood_cost = fields.Float('Total')
    net_cubic_change = fields.Float('Net Cubic (M3)')
    unit_wood_change = fields.Float('Unit Wood Cost')
    unit_labour_change = fields.Float('Unit Labour Cost')
    total_wood_change = fields.Float('Total')

    oil_paint_cost = fields.Float('Oil & Paint')
    hardware_cost = fields.Float('Hardware')
    special_hardware_cost = fields.Float('Special Hardware')
    canvas_cost = fields.Float('Canvas')
    packing_cost = fields.Float('Packing')
    total_other_material_cost = fields.Float('Total')
    oil_paint_change = fields.Float('Oil & Paint')
    hardware_change = fields.Float('Hardware')
    special_hardware_change = fields.Float('Special Hardware')
    canvas_change = fields.Float('Canvas')
    packing_change = fields.Float('Packing')
    total_other_material_change = fields.Float('Total')
    
    wood_cost = fields.Float('Wood*15%')
    hd_cost = fields.Float('H,D.*35%')
    canvas_cost_15 = fields.Float('Canvas*15%')
    load = fields.Float('Load 40 Max')
    load_cost = fields.Float('Proportion/Load')
    total_overhead_cost = fields.Float('Total')
    wood_change = fields.Float('Wood*15%')
    hd_change = fields.Float('H,D.*35%')
    canvas_change_15 = fields.Float('Canvas*15%')
    load_change = fields.Float('$550/Load')
    total_overhead_change = fields.Float('Total')
    
    product_cost = fields.Float('Product Cost')
    product_change = fields.Float('Product Cost')

    selling_price = fields.Float('Selling Price')
    commision_percent = fields.Float('Commision %')
    commision = fields.Float('Commision',compute='_compute_commision')
    net_profit = fields.Float('Net Profit',compute='_compute_net_profit')
    net_profit_percent = fields.Float('Net Profit (%)',compute='_compute_net_profit')

    @api.depends('commision_percent','selling_price')
    def _compute_commision(self):
        for rec in self:
            rec.commision = round(rec.selling_price * rec.commision_percent / 100,2)

    @api.depends('selling_price','product_cost','commision')
    def _compute_net_profit(self):
        for rec in self:
            rec.net_profit = round(rec.selling_price - rec.product_cost - rec.commision,2)
            res = 0.00
            if rec.selling_price > 0:
                res = round(rec.net_profit / rec.selling_price * 100,2)
            rec.net_profit_percent = res

    approved_user_id = fields.Many2one('res.users', string='Approved By')
    assessed_user_id = fields.Many2one('res.users', string='Assessed By')
    calculated_user_id = fields.Many2one('res.users', string='Calculated By')
    ship_date = fields.Date('Ship Date')

class WoodCostingLine(models.Model):
    _name = 'wood.costing.line'
    _description = 'Wood Costing Line'
    
    summary_costing_id = fields.Many2one('summary.costing', string='Summary Costing')
    product_id = fields.Many2one('product.product', 'Componen')
    component_size_p = fields.Float("Comp't P")
    component_size_l = fields.Float("Comp't L")
    component_size_t = fields.Float("Comp't T")
    qty = fields.Float('Qty')
    act_price = fields.Float("A'L Price",digits=(12,2))
    # act_cost = fields.Float("A'L Cost",digits=(12,2))
    currency = fields.Selection([
        ('RP', 'RP'),
        ('NT', 'NT'),
        ('RMB', 'RMB'),
        ('USA', 'USA'),
    ], string='Currency',default='RP')
    price_currency = fields.Float('Price Currency')

    net_cubic = fields.Float(compute='_compute_net_cubic', string='Net Cubic',digits=(12,5))
    wood_price = fields.Float(compute='_compute_wood_price', string='Wood Price',digits=(12,2))
    component_price = fields.Float(compute='_compute_component_price', string='Component Price',digits=(12,2))
    
    act_cost = fields.Float(compute='_compute_act_cost', string="A'L Cost")

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.price_currency = self.product_id.standard_price
    

    @api.depends('qty','act_price')
    def _compute_act_cost(self):
        for rec in self:
            rec.act_cost = rec.qty * rec.act_price

    @api.depends('net_cubic','wood_price')
    def _compute_component_price(self):
        for rec in self:
            rec.component_price = round(rec.net_cubic * rec.wood_price,2)
    
    @api.depends('currency','price_currency','summary_costing_id.rp_exchange_rate','summary_costing_id.nt_exchange_rate','summary_costing_id.rmb_exchange_rate')
    def _compute_wood_price(self):
        for rec in self:
            res = rec.price_currency
            if rec.currency == 'RP':
                if rec.summary_costing_id.rp_exchange_rate > 0:
                    res = round(7500000 / rec.summary_costing_id.rp_exchange_rate,3)
            if rec.currency == 'NT':
                if rec.summary_costing_id.nt_exchange_rate > 0:
                    res = round(7500000 / rec.summary_costing_id.nt_exchange_rate,3)
            if rec.currency == 'RMB':
                if rec.summary_costing_id.rmb_exchange_rate > 0:
                    res = round(7500000 / rec.summary_costing_id.rmb_exchange_rate,3)
            rec.wood_price = res

    @api.depends('component_size_p','component_size_l','component_size_t','qty')
    def _compute_net_cubic(self):
        for rec in self:
            rec.net_cubic = round((rec.component_size_p * rec.component_size_l * rec.component_size_t) / 1000000000 * rec.qty,5)

class HardwareCostingLine(models.Model):
    _name = 'hardware.costing.line'
    _description = 'Hardware Costing Line'

    product_id = fields.Many2one('product.product', 'Item')
    summary_costing_id = fields.Many2one('summary.costing', string='Summary Costing')
    code = fields.Char('Code No.')
    desc = fields.Char('Description')
    qty = fields.Float('Qty')
    currency = fields.Selection([
        ('RP', 'RP'),
        ('NT', 'NT'),
        ('RMB', 'RMB'),
        ('USA', 'USA'),
    ], string='Currency',default='RP')
    price_currency = fields.Float('Price Currency')
    act_price = fields.Float("A'L Price")
    change = fields.Float('Change %', store=True, compute='_compute_change')

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.price_currency = self.product_id.standard_price

    @api.depends('cost')
    def _compute_change(self):
            total_cost = sum(self.mapped('cost'))
            for record in self:
                record.change = record.cost / total_cost * 100 if total_cost else 0
    
    # unit_price = fields.Float(compute='_compute_unit_price', string='Unit Price (US$)',digits=(12,3))
    unit_price = fields.Float(compute='_compute_unit_price', string='Unit Price (Rp)',digits=(12,3))

    cost = fields.Float(compute='_compute_cost', string='cost')
    act_cost = fields.Float(compute='_compute_act_cost', string="A'L Cost")

    @api.depends('qty','act_price')
    def _compute_act_cost(self):
        for rec in self:
            rec.act_cost = rec.qty * rec.act_price
    
    @api.depends('qty','unit_price')
    def _compute_cost(self):
        for rec in self:
            rec.cost = rec.qty * rec.unit_price

    @api.depends('qty','currency','price_currency','summary_costing_id.rp_exchange_rate','summary_costing_id.nt_exchange_rate','summary_costing_id.rmb_exchange_rate')
    def _compute_unit_price(self):
        for rec in self:
            res = rec.price_currency
            if rec.currency == 'USA':
                if rec.summary_costing_id.usa_exchange_rate > 0:
                    res = round(rec.price_currency * rec.summary_costing_id.usa_exchange_rate,3)
            if rec.currency == 'RP':
                if rec.summary_costing_id.rp_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.rp_exchange_rate,3)
            if rec.currency == 'NT':
                if rec.summary_costing_id.nt_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.nt_exchange_rate,3)
            if rec.currency == 'RMB':
                if rec.summary_costing_id.rmb_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.rmb_exchange_rate,3)
            rec.unit_price = res

class SpesialsMaterialCostingLine(models.Model):
    _name = 'spesials.material.costing.line'
    _description = 'Spesials Material Costing Line'
    
    summary_costing_id = fields.Many2one('summary.costing', string='Summary Costing')

    product_id = fields.Many2one('product.product', 'Item')

    code = fields.Char('Code No.')
    desc = fields.Char('Description')
    qty = fields.Float('Qty')
    currency = fields.Selection([
        ('RP', 'RP'),
        ('NT', 'NT'),
        ('RMB', 'RMB'),
        ('USA', 'USA'),
    ], string='Currency',default='RP')
    price_currency = fields.Float('Price Currency')

 
    act_price = fields.Float("A'L Unit Cost")
    # change = fields.Float('Change %')

    cost = fields.Float(compute='_compute_cost', string='Cost')
    act_cost = fields.Float(compute='_compute_act_cost', string="A'L Cost")
    change = fields.Float('Change %', store=True, compute='_compute_change')

    unit_price = fields.Float('Unit Price', 
        compute='_compute_unit_price' )

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.price_currency = self.product_id.standard_price

    @api.depends('price_currency')
    def _compute_unit_price(self):
        for record in self:
            record.unit_price = self.price_currency

    @api.depends('cost')
    def _compute_change(self):
            total_cost = sum(self.mapped('cost'))
            for record in self:
                record.change = record.cost / total_cost * 100 if total_cost else 0

    @api.depends('qty','act_price')
    def _compute_act_cost(self):
        for rec in self:
            rec.act_cost = rec.qty * rec.act_price

    @api.depends('qty','unit_price')
    def _compute_cost(self):
        for rec in self:
            rec.cost = rec.qty * rec.unit_price

    @api.depends('currency','price_currency','summary_costing_id.rp_exchange_rate','summary_costing_id.nt_exchange_rate','summary_costing_id.rmb_exchange_rate')
    def _compute_unit_price(self):
        for rec in self:
            res = rec.price_currency
            if rec.currency == 'RP':
                if rec.summary_costing_id.rp_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.rp_exchange_rate,3)
            if rec.currency == 'NT':
                if rec.summary_costing_id.nt_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.nt_exchange_rate,3)
            if rec.currency == 'RMB':
                if rec.summary_costing_id.rmb_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.rmb_exchange_rate,3)
            rec.unit_price = res


class CanvasCostingLine(models.Model):
    _name = 'canvas.costing.line'
    _description = 'Canvas Costing Line'
    
    summary_costing_id = fields.Many2one('summary.costing', string='Summary Costing')
    product_id = fields.Many2one('product.product', 'Material')

    material = fields.Char('Material')
    usage = fields.Float('Usage')
    currency = fields.Selection([
        ('RP', 'RP'),
        ('NT', 'NT'),
        ('RMB', 'RMB'),
        ('USA', 'USA'),
    ], string='Currency',default='RP')
    price_currency = fields.Float('Price Currency')
    # unit_price = fields.Float('Unit Price')
    act_price = fields.Float("A'L Unit Cost")
    # change = fields.Float('Change %')

    cost = fields.Float(compute='_compute_cost', string='Cost')
    act_cost = fields.Float(compute='_compute_act_cost', string="A'L Cost")

    change = fields.Float('Change %', store=True, compute='_compute_change')

    unit_price = fields.Float('Unit Price', 
        compute='_compute_unit_price' )

    @api.depends('price_currency')
    def _compute_unit_price(self):
        for record in self:
            record.unit_price = self.price_currency

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.price_currency = self.product_id.standard_price

    @api.depends('cost')
    def _compute_change(self):
            total_cost = sum(self.mapped('cost'))
            for record in self:
                record.change = record.cost / total_cost * 100 if total_cost else 0

    @api.depends('usage','act_price')
    def _compute_act_cost(self):
        for rec in self:
            rec.act_cost = rec.usage * rec.act_price

    @api.depends('usage','unit_price')
    def _compute_cost(self):
        for rec in self:
            rec.cost = rec.usage * rec.unit_price

    @api.depends('currency','price_currency','summary_costing_id.rp_exchange_rate','summary_costing_id.nt_exchange_rate','summary_costing_id.rmb_exchange_rate')
    def _compute_unit_price(self):
        for rec in self:
            res = rec.price_currency
            if rec.currency == 'RP':
                if rec.summary_costing_id.rp_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.rp_exchange_rate,3)
            if rec.currency == 'NT':
                if rec.summary_costing_id.nt_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.nt_exchange_rate,3)
            if rec.currency == 'RMB':
                if rec.summary_costing_id.rmb_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.rmb_exchange_rate,3)
            rec.unit_price = res

class PackingCostingLine(models.Model):
    _name = 'packing.costing.line'
    _description = 'Packing Costing Line'
    
    summary_costing_id = fields.Many2one('summary.costing', string='Summary Costing')
    product_id = fields.Many2one('product.product', 'Material')

    material = fields.Char('Material')
    model = fields.Char('Model')
    qty = fields.Float('Qty')
    currency = fields.Selection([
        ('RP', 'RP'),
        ('NT', 'NT'),
        ('RMB', 'RMB'),
        ('USA', 'USA'),
    ], string='Currency',default='RP')
    price_currency = fields.Float('Price Currency')
    # unit_price = fields.Float('Cost Per CTN')
    act_price = fields.Float("A'L Unit Cost")
    # change = fields.Float('Change %')

    cost = fields.Float(compute='_compute_cost', string='Cost')
    act_cost = fields.Float(compute='_compute_act_cost', string="A'L Cost")

    change = fields.Float('Change %', store=True, compute='_compute_change')

    unit_price = fields.Float('Cost Per CTN', 
        compute='_compute_unit_price' )
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        self.price_currency = self.product_id.standard_price


    @api.depends('price_currency')
    def _compute_unit_price(self):
        for record in self:
            record.unit_price = self.price_currency


    @api.depends('cost')
    def _compute_change(self):
            total_cost = sum(self.mapped('cost'))
            for record in self:
                record.change = record.cost / total_cost * 100 if total_cost else 0

    @api.depends('qty','act_price')
    def _compute_act_cost(self):
        for rec in self:
            rec.act_cost = rec.qty * rec.act_price

    @api.depends('qty','unit_price')
    def _compute_cost(self):
        for rec in self:
            rec.cost = rec.qty * rec.unit_price

    @api.depends('currency','price_currency','summary_costing_id.rp_exchange_rate','summary_costing_id.nt_exchange_rate','summary_costing_id.rmb_exchange_rate')
    def _compute_unit_price(self):
        for rec in self:
            res = rec.price_currency
            if rec.currency == 'RP':
                if rec.summary_costing_id.rp_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.rp_exchange_rate,3)
            if rec.currency == 'NT':
                if rec.summary_costing_id.nt_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.nt_exchange_rate,3)
            if rec.currency == 'RMB':
                if rec.summary_costing_id.rmb_exchange_rate > 0:
                    res = round(rec.price_currency / rec.summary_costing_id.rmb_exchange_rate,3)
            rec.unit_price = res