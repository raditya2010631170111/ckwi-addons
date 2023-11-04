from odoo import models, fields, api, _
from odoo.exceptions import UserError

class design_processSH(models.Model):
    _inherit = 'design.process'

    def get_costing_bom(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Summary Costing',
            'view_mode': 'tree,form',
            'res_model': 'summary.costing',
            'domain': [('rnd_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def action_costing(self):
        for res in self:
            if not res.spec_design_ids:
                raise UserError("Spec Design Not Found")

            for line in res.spec_design_ids:
                actual_cost = []
                wood_component = []
                hardware = []
                print(line.item_id.id, "hahagg")
                bom_ids = res.env['mrp.bom'].search(['|', ('product_id', '=', line.item_id.id), '&', ('product_id', '=', False), ('product_tmpl_id', '=', line.item_id.product_tmpl_id.id)])
                print(bom_ids, "haha2")
                for bom in bom_ids:
                    print(bom,"id bom")
                    print(bom.product_tmpl_id.id, "id bom2")
                    for component in bom.bom_line_ids:
                        actual_cost.append((0,0,{
                            'product_tmpl_id': bom.product_tmpl_id.id,
                            'product_id': component.product_id.id,
                            }))

                        if component.product_id.type_rnd == "component":
                            wood_component.append((0, 0, {
                                'product_tmpl_id': bom.product_tmpl_id.id,
                                'product_id': component.product_id.id,
                                'qty': component.product_qty,
                                'component_size_p': bom.product_tmpl_id.size_panjang,
                                'component_size_l': bom.product_tmpl_id.size_lebar,
                                'component_size_t': bom.product_tmpl_id.size_tebal,
                            }))

                        if component.product_id.type_rnd == "hardware":
                            hardware.append((0, 0, {
                                'product_tmpl_id': bom.product_tmpl_id.id,
                                'product_id': component.product_id.id,
                                'qty': component.product_qty,
                                'code': '-',
                                'desc': '-',
                            }))

                design = {
                    'rnd_id': res.id,
                    'item_no': res.item.name,
                    'item_id': line.item_id.id,
                    'item_description': line.item_id.description,
                    'request_no' : res.request_no,
                    'wood_costing_line_ids': wood_component,
                    'actual_costing_line_ids': actual_cost,
                    'hadware_costing_line_ids': hardware,
                    'detail_material_ids': res.detail_material_ids,
                }
                print(design)
                cost = self.env['summary.costing']
                cost.create(design)

class SummaryCostingSH(models.Model):
    _inherit = 'summary.costing'

    detail_material_ids = fields.Many2many('design.material', 'masterial_ref_name_matrial_costing', 'material_rgt_name_id',
                                           'material_ref_name_costing_id', 'Wood')


# class MrpBomSH(models.Model):
#     _inherit = 'mrp.bom'
#
#     type_rnd = fields.Selection([
#         ('component', 'Component'),
#         ('hardware', 'Hardware')],
#         string='Type RDN', default='component')

class ProductProductSH(models.Model):
    _inherit = 'product.product'

    type_rnd = fields.Selection([
        ('component', 'Component'),
        ('hardware', 'Hardware')],
        string='Type R&D', default='component')


class WoodCostingLineSH(models.Model):
    _inherit = 'wood.costing.line'

    product_tmpl_id = fields.Many2one('product.template', 'Componen Tmpl')


class ActualCostingLineSH(models.Model):
    _inherit = 'actual.costing.line'

    product_tmpl_id = fields.Many2one('product.template', 'Componen Tmpl')
    total_wood_cost = fields.Float('Total', compute='_compute_total_wood_cost', digits=(12,2))
    total_overhead_cost = fields.Float('Total', compute='_compute_total_overhead_cost', digits=(12,2))
    total_other_material_cost = fields.Float('Total', compute='_compute_total_other_material_cost', digits=(12,2))
    product_cost = fields.Float('Product Cost', compute='_compute_product_cost', digits=(12,2), readonly=True)
    product_change = fields.Float('Product Cost', readonly=True)

    # change
    net_cubic_change = fields.Float('Net Cubic (M3)', compute='_compute_change', readonly=True)
    unit_wood_change = fields.Float('Unit Wood Cost', compute='_compute_change', readonly=True)
    unit_labour_change = fields.Float('Unit Labour Cost', compute='_compute_change', readonly=True)
    total_wood_change = fields.Float('Total', compute='_compute_change', readonly=True)
    oil_paint_change = fields.Float('Oil & Paint', compute='_compute_change', readonly=True)
    hardware_change = fields.Float('Hardware', compute='_compute_change', readonly=True)
    special_hardware_change = fields.Float('Special Hardware', compute='_compute_change', readonly=True)
    canvas_change = fields.Float('Canvas', compute='_compute_change', readonly=True)
    packing_change = fields.Float('Packing', compute='_compute_change', readonly=True)
    total_other_material_change = fields.Float('Total', compute='_compute_change', readonly=True)
    total_overhead_change = fields.Float('Total', compute='_compute_change', readonly=True)

    # cost

    @api.depends('net_cubic_cost', 'unit_wood_cost', 'unit_labour_cost', 'product_cost')
    def _compute_total_wood_cost(self):
        for rec in self:
            rec.total_wood_cost = round(rec.net_cubic_cost+rec.unit_wood_cost+rec.unit_labour_cost, 2)

    @api.depends('oil_paint_cost', 'hardware_cost', 'special_hardware_cost', 'canvas_cost', 'packing_cost')
    def _compute_total_other_material_cost(self):
        for rec in self:
            rec.total_other_material_cost = round(rec.oil_paint_cost+rec.hardware_cost+rec.special_hardware_cost+rec.canvas_cost+rec.packing_cost, 2)

    @api.depends('wood_cost', 'hd_cost', 'canvas_cost_15', 'load', 'load_cost')
    def _compute_total_overhead_cost(self):
        for rec in self:
            rec.total_overhead_cost = round(rec.wood_cost+rec.hd_cost+rec.canvas_cost_15+rec.load+rec.load_cost, 2)

    @api.depends('total_wood_cost', 'total_other_material_cost', 'total_overhead_cost')
    def _compute_product_cost(self):
        for rec in self:
            rec.product_cost = round(rec.total_wood_cost+rec.total_other_material_cost+rec.total_overhead_cost, 2)

    # change
    @api.depends('product_cost')
    def _compute_change(self):
        for rec in self:
            rec.product_change = 100
            # change wood cost
            net_cubic_cost = rec.net_cubic_cost / rec.product_cost if rec.net_cubic_cost > 0 else 0.00
            rec.net_cubic_change = round(net_cubic_cost * 100, 2)
            unit_wood_cost = rec.unit_wood_cost / rec.product_cost if rec.unit_wood_cost > 0 else 0.00
            rec.unit_wood_change = round(unit_wood_cost * 100, 2)
            unit_labour_cost = rec.unit_labour_cost / rec.product_cost if rec.unit_labour_cost > 0 else 0.00
            rec.unit_labour_change = round(unit_labour_cost * 100, 2)
            total_wood_cost = rec.total_wood_cost / rec.product_cost if rec.total_wood_cost > 0 else 0.00
            rec.total_wood_change = round(total_wood_cost * 100, 2)

            # change other material
            oil_paint_cost = rec.oil_paint_cost / rec.product_cost if rec.oil_paint_cost > 0 else 0.00
            rec.oil_paint_change = round(oil_paint_cost * 100, 2)
            hardware_cost = rec.hardware_cost / rec.product_cost if rec.hardware_cost > 0 else 0.00
            rec.hardware_change = round(hardware_cost * 100, 2)
            special_hardware_cost = rec.special_hardware_cost / rec.product_cost if rec.special_hardware_cost > 0 else 0.00
            rec.special_hardware_change = round(special_hardware_cost * 100, 2)
            canvas_cost = rec.canvas_cost / rec.product_cost if rec.canvas_cost > 0 else 0.00
            rec.canvas_change = round(canvas_cost * 100, 2)
            packing_cost = rec.packing_cost / rec.product_cost if rec.packing_cost > 0 else 0.00
            rec.packing_change = round(packing_cost * 100, 2)
            total_other_material_cost = rec.total_other_material_cost / rec.product_cost if rec.total_other_material_cost > 0 else 0.00
            rec.total_other_material_change = round(total_other_material_cost * 100, 2)

            # change overhead
            total_overhead_cost = rec.total_overhead_cost / rec.product_cost if rec.total_overhead_cost > 0 else 0.00
            rec.total_overhead_change = round(total_overhead_cost * 100, 2)










class HardwareCostingLineSH(models.Model):
    _inherit = 'hardware.costing.line'

    product_tmpl_id = fields.Many2one('product.template', 'Componen Tmpl')


# class SaleOrderLineSH(models.Model):
#     _inherit = 'sale.order.line'
#
#     detail_material_ids = fields.Many2many('design.material', 'masterial_ref_name_matrial_so',
#                                            'material_rgt_name_id',
#                                            'material_ref_name_so_id', 'Material Finishing')
#
#     detail_finish_ids = fields.Many2many('design.finish', 'design_ref_name_finish_so', 'design_ref_id',
#                                          'name_fish_finish_so_id', 'Finish')
#
#     @api.onchange("product_id")
#     def _set_fill_from_costing(self):
#         for res in self:
#             print(res.product_id.id)
#             if res.product_id.id:
#                 get_spec_design = res.env["spec.design"].search([("item_id", "=", res.product_id.id)], limit=1, order="id desc")
#                 if get_spec_design:
#                     get_design_process = res.env["design.process"].search(
#                         [("id", "=", get_spec_design.design_process_id.id)], limit=1,
#                         order="id desc")
#                     get_costing = res.env["summary.costing"].search([("rnd_id", "=", get_spec_design.design_process_id.id)], limit=1, order="id desc")
#                     res.canvas = get_costing.canvas_cost
#                     res.detail_material_ids = get_design_process.detail_material_ids
#                     res.detail_finish_ids = get_design_process.detail_finish_ids
#                     res.packing = sum([x.packing_cost for x in get_costing.actual_costing_line_ids])
#
#                 res.packing_size_p = get_spec_design.item_id.product_tmpl_id.size_panjang
#                 res.packing_size_l = get_spec_design.item_id.product_tmpl_id.size_lebar
#                 res.packing_size_t = get_spec_design.item_id.product_tmpl_id.size_tebal
#             # print(get_spec_design.attachment)
#             # res.attachment = get_spec_design.attachment
#             # res.name = get_spec_design.description






