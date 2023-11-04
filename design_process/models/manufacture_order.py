
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_round


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'
    _description = 'BOM Structure Report'


    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        bom = self.env['mrp.bom'].browse(bom_id)
        company = bom.company_id or self.env.company
        
        bom_quantity = line_qty
        if line_id:
            current_line = self.env['mrp.bom.line'].browse(int(line_id))
            bom_quantity = current_line.product_uom_id._compute_quantity(line_qty, bom.product_uom_id) or 0
        # Display bom components for current selected product variant
        if product_id:
            product = self.env['product.product'].browse(int(product_id))
            total_meter = product.total_meter * bom_quantity
            total_meter_cubic = product.total_meter_cubic * bom_quantity
            total_meter_persegi = product.total_meter_persegi * bom_quantity

        else:
            product = bom.product_id or bom.product_tmpl_id.product_variant_id
            product_tmpl = bom.product_tmpl_id
            product = product_tmpl.product_variant_id
            total_meter = product_tmpl.total_meter * bom_quantity
            total_meter_cubic = product_tmpl.total_meter_cubic * bom_quantity
            total_meter_persegi = product_tmpl.total_meter_persegi * bom_quantity
            
        if product:
            price = product.uom_id._compute_price(product.with_company(company).standard_price, bom.product_uom_id) * bom_quantity
            attachments = self.env['mrp.document'].search(['|', '&', ('res_model', '=', 'product.product'),
            ('res_id', '=', product.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', product.product_tmpl_id.id)])
        else:
            # Use the product template instead of the variant
            price = bom.product_tmpl_id.uom_id._compute_price(bom.product_tmpl_id.with_company(company).standard_price, bom.product_uom_id) * bom_quantity
            attachments = self.env['mrp.document'].search([('res_model', '=', 'product.template'), ('res_id', '=', bom.product_tmpl_id.id)])
        operations = self._get_operation_line(bom, float_round(bom_quantity, precision_rounding=1, rounding_method='UP'), 0)
        lines = {
            'bom': bom,
            'bom_qty': bom_quantity,
            'bom_prod_name': product.display_name,
            'currency': company.currency_id,
            'product': product,
            'code': bom and bom.display_name or '',
            'price': price,
            'total': sum([op['total'] for op in operations]),
            'level': level or 0,
            'operations': operations,
            'operations_cost': sum([op['total'] for op in operations]),
            'attachments': attachments,
            'operations_time': sum([op['duration_expected'] for op in operations]),
            'prod_panjang': bom.size_panjang,
            'prod_lebar': bom.size_lebar,
            'prod_tebal': bom.size_tebal,
            'total_meter_cubic': total_meter_cubic,
            'total_meter_persegi': total_meter_persegi,
            'ratio': bom.ratio,
            'desc': bom.desc,
            'total_meter': total_meter,
        }
        components, total = self._get_bom_lines(bom, bom_quantity, product, line_id, level)
        lines['components'] = components
        lines['total'] += total
        return lines

    def _get_bom_lines(self, bom, bom_quantity, product, line_id, level):
        components = []
        total = 0

        for line in bom.bom_line_ids:
            
            line_quantity = (bom_quantity / (bom.product_qty or 1.0)) * line.product_qty
            if line._skip_bom_line(product):
                continue
            company = bom.company_id or self.env.company
            price = line.product_id.uom_id._compute_price(line.product_id.with_company(company).standard_price, line.product_uom_id) * line_quantity
            if line.child_bom_id:
                
                factor = line.product_uom_id._compute_quantity(line_quantity, line.child_bom_id.product_uom_id) / line.child_bom_id.product_qty
                sub_total = self._get_price(line.child_bom_id, factor, line.product_id)
            else:
                sub_total = price
            sub_total = self.env.company.currency_id.round(sub_total)
            prod = line.product_id.product_tmpl_id.id
            components.append({
                'prod': prod,
                'prod_id': line.product_id.id,
                'prod_name': line.product_id.display_name,
                'code': line.child_bom_id and line.child_bom_id.display_name or '',
                'prod_qty': line_quantity,
                'prod_uom': line.product_uom_id.name,
                'prod_cost': company.currency_id.round(price),
                'parent_id': bom.id,
                'line_id': line.id,
                'level': level or 0,
                'total': sub_total,
                'child_bom': line.child_bom_id.id,
                'phantom_bom': line.child_bom_id and line.child_bom_id.type == 'phantom' or False,
                'prod_panjang': line.size_panjang,
                'prod_lebar': line.size_lebar,
                'prod_tebal': line.size_tebal,
                'total_meter_cubic': (line.total_meter_cubic * bom_quantity) / bom.product_qty or 1.0 , 
                'total_meter_persegi': (line.total_meter_persegi * bom_quantity) / bom.product_qty or 1.0 ,
                'attachments': self.env['mrp.document'].search(['|', '&',
                    ('res_model', '=', 'product.product'), ('res_id', '=', line.product_id.id), '&', ('res_model', '=', 'product.template'), ('res_id', '=', line.product_id.product_tmpl_id.id)]),
                'total_meter1':  (line.total_meter1 * bom_quantity) / bom.product_qty or 1.0 ,
                'total_meter_cubic1': (line.total_meter_cubic1 * bom_quantity) / bom.product_qty or 1.0 ,
                'total_meter_persegi1': (line.total_meter_persegi1 * bom_quantity) / bom.product_qty or 1.0

            })
            total += sub_total
        return components, total

    def _get_pdf_line(self, bom_id, product_id=False, qty=1, child_bom_ids=[], unfolded=False):

        def get_sub_lines(bom, product_id, line_qty, line_id, level):
            data = self._get_bom(bom_id=bom.id, product_id=product_id, line_qty=line_qty, line_id=line_id, level=level)
            bom_lines = data['components']
            lines = []
            for bom_line in bom_lines:
                lines.append({
                    'name': bom_line['prod_name'],
                    'type': 'bom',
                    'quantity': bom_line['prod_qty'],
                    'uom': bom_line['prod_uom'],
                    'prod_cost': bom_line['prod_cost'],
                    'bom_cost': bom_line['total'],
                    'level': bom_line['level'],
                    'code': bom_line['code'],
                    'child_bom': bom_line['child_bom'],
                    'prod_id': bom_line['prod_id'],
                    'prod_panjang': bom_line['prod_panjang'],
                    'prod_lebar': bom_line['prod_lebar'],
                    'prod_tebal': bom_line['prod_tebal'],
                    'total_meter_cubic1': bom_line['total_meter_cubic1'],
                    'total_meter_persegi1': bom_line['total_meter_persegi1'],
                    'total_meter1': bom_line['total_meter1'],
                })
                if bom_line['child_bom'] and (unfolded or bom_line['child_bom'] in child_bom_ids):
                    line = self.env['mrp.bom.line'].browse(bom_line['line_id'])
                    lines += (get_sub_lines(line.child_bom_id, line.product_id.id, bom_line['prod_qty'], line, level + 1))
            if data['operations']:
                lines.append({
                    'name': _('Operations'),
                    'type': 'operation',
                    'quantity': data['operations_time'],
                    'uom': _('minutes'),
                    'bom_cost': data['operations_cost'],
                    'level': level,
                    'prod_panjang': False,
                    'prod_lebar': False,
                    'prod_tebal': False,
                    'total_meter_cubic': False,
                    'total_meter_persegi': False,
                })
                for operation in data['operations']:
                    if unfolded or 'operation-' + str(bom.id) in child_bom_ids:
                        lines.append({
                            'name': operation['name'],
                            'type': 'operation',
                            'quantity': operation['duration_expected'],
                            'uom': _('minutes'),
                            'bom_cost': operation['total'],
                            'level': level + 1,
                            'prod_panjang': False,
                            'prod_lebar': False,
                            'prod_tebal': False,
                            'total_meter_cubic': False,
                            'total_meter_persegi': False,
                        })
            return lines

        bom = self.env['mrp.bom'].browse(bom_id)
        product_id = product_id or bom.product_id.id or bom.product_tmpl_id.product_variant_id.id
        data = self._get_bom(bom_id=bom_id, product_id=product_id, line_qty=qty)
        pdf_lines = get_sub_lines(bom, product_id, qty, False, 1)
        data['components'] = []
        data['lines'] = pdf_lines
        return data



class JidokaManufacturingOrder(models.Model):
    _inherit = 'mrp.production'
    _description = 'Spec Design'


    request_no = fields.Char("No. Spec Design",readonly=True)
    rnd_id = fields.Many2one("design.process","RnD", readonly=True)
    # work_order_ids = fields.Many2many('mrp.workorder', string='Work Order', 
    #     compute='_compute_work_order_ids' )
    workcenter = fields.Char('Work Center Char',
        compute='_compute_workcenter', store=True)
    
    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center', 
        compute='_compute_workcenter_id', store=True)
    
    qty_producing = fields.Float(string="Quantity Producing", digits='Product Unit of Measure', copy=False, tracking=True)

    
    @api.depends('workcenter')
    def _compute_workcenter_id(self):
        for r in self:
            # workorder_ids = r.env['mrp.workorder'].search([('production_id','=',r.id)]).mapped('workcenter_id')[0]
            workorder_id = r.env['mrp.workcenter'].search([('name','=',r.workcenter)])
            r.workcenter_id = workorder_id.id
    
    @api.depends('workorder_ids.workcenter_id')
    def _compute_workcenter(self):
        for r in self:
            workcenter = ''
            if r.workorder_ids:
                for wo in r.workorder_ids[0]:
                    # workcenter += wo.workcenter_id.name + ','
                    # workcenter += wo.workcenter_id.name 
                    workcenter = wo.workcenter_id.name 
                
            r.workcenter = workcenter

    
    
    
    
    # @api.depends('depends')
    # def _compute_work_order_ids(self):
    #     for r in self:
    #         workorder_ids = self.env['mrp.workorder'].search([('production_id','=',r.id)])
    #         r.work_order_ids = workorder_ids
            # r.work_center_ids = something
    
    
    


    def _get_moves_finished_values(self):
        moves = []
        for production in self:
            if production.product_id in production.bom_id.byproduct_ids.mapped('product_id'):
                raise UserError(_("You cannot have %s  as the finished product and in the Byproducts", production.product_id.name))
            moves.append(production._get_move_finished_values(production.product_id.id, production.product_qty, production.product_uom_id.id))
            for byproduct in production.bom_id.byproduct_ids:
                product_uom_factor = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id)
                qty = byproduct.product_qty * (product_uom_factor / production.bom_id.product_qty)
                moves.append(production._get_move_finished_values(
                    byproduct.product_id.id, qty, byproduct.product_uom_id.id,
                    byproduct.operation_id.id, byproduct.id))
        return moves








class JidokaManufacturingBoM(models.Model):
    _inherit = 'mrp.bom'
    _description = 'Spec Design'


    crm_id = fields.Many2one("crm.lead","Oportunity",readonly=True)
    rnd_id = fields.Many2one("design.process","RnD", readonly=True)
    qty_so = fields.Integer("Quantity SO")
    uom_so = fields.Many2one("uom.uom","UoM SO")
    size_tebal = fields.Integer("Size Tebal", compute="get_kubikasi", store=True, readonly=False)
    size_lebar = fields.Integer("Size Lebar", compute="get_kubikasi", store=True, readonly=False)
    size_panjang = fields.Integer("Size Panjang", compute="get_kubikasi", store=True, readonly=False)
    total_meter_cubic = fields.Float("Meter Cubic (M³)", digits=(12,5), store=True, related='product_id.total_meter_cubic')
    total_meter_persegi = fields.Float("Meter Persegi (M²)", digits=(12,5), store=True,related='product_id.total_meter_persegi') #compute="_get_calc",
    # total_meter = fields.Float("Meter (M)", digits=(12,8), store=True, related='product_id.total_meter')
    ratio = fields.Integer("Rasio")
    desc = fields.Char("Catatan")
    attachments = fields.Binary('Attachments')
    is_product_componen = fields.Boolean("Is Product Componen", related='product_tmpl_id.is_componen')
    type_bom = fields.Selection([
        ('is_sample', 'Is Sample Request'),
        ('is_design', 'Is Spec Design')],
        string='Type BoM', copy=True)
   


    @api.depends("product_tmpl_id")
    def get_kubikasi(self):
        for tc in self:
            kbc = tc.product_tmpl_id
            tc.size_tebal = kbc.size_tebal
            tc.size_panjang = kbc.size_panjang
            tc.size_lebar = kbc.size_lebar
            tc.total_meter_cubic = kbc.total_meter_cubic
            tc.total_meter_persegi = kbc.total_meter_persegi
            tc.uom_so = kbc.uom_id.id

    # @api.depends('size_panjang', 'size_lebar','size_tebal','qty_so','ratio')
    # def _get_calc(self):
    #     for cal in self:
    #         meter = cal.size_panjang * cal.size_lebar * cal.size_tebal
    #         total_meter_cubic = (meter) / 1000000000 if meter > 0 else 0.00
    #         total_meter_persegi = (meter) / 1000000 if meter > 0 else 0.00
    #         total_rasio = (cal.qty_so * cal.ratio)
    #         cal.total_meter_cubic = total_rasio * total_meter_cubic
    #         cal.total_meter_persegi = total_rasio * total_meter_persegi



class JidokaManufacturingBoMLine(models.Model):
    _inherit = 'mrp.bom.line'
    _description = 'Spec Design'
    
    standard_price = fields.Float(related='product_id.standard_price', string="Cost",
    readonly=False, 
    required=False
    )
    sub_cost = fields.Float('Subtotal Cost', digits='Product Unit of Measure', store=True, compute='_compute_sub_cost')
    product_id = fields.Many2one('product.product', 'Component')
    product_tmpl_id = fields.Many2one ('product.template', 'Product Template')
    kubikasi_id = fields.Many2one("product.kubikasi","Kubikasi")
    size_panjang = fields.Float("P" , 
    store=True,related='product_tmpl_id.size_panjang')
    model = fields.Char('Model', related='product_tmpl_id.model', store=True)
    size_lebar = fields.Float("L", 
    store=True, related='product_tmpl_id.size_lebar'
    )

    size_tebal = fields.Float("T", 
    store=True,related='product_tmpl_id.size_tebal'
    )

    total_meter_cubic = fields.Float("Cubic (M³)", digits=(12,5), 
    store=True
    )
    total_meter_cubic1 = fields.Float("Cubic (M³)", digits=(12,5), 
    store=True, compute="get_calc_mcubic1"
    )
    total_meter_persegi = fields.Float("Persegi (M²)", digits=(12,5), 
    store=True
    )
    total_meter_persegi1 = fields.Float("Persegi (M²)", digits=(12,5), 
    store=True, compute="get_calc_mpersegi1"
    )
    total_meter = fields.Float("Meter (M)", digits=(12,5), store=True)
    total_meter1 = fields.Float("Meter (M)", digits=(12,5), store=True, compute="get_calc_meter1")
    product_code = fields.Char('Code', related='product_id.product_code', store=True)
    description = fields.Char("Description", store=True)

    @api.depends('standard_price', 'product_qty')
    def _compute_sub_cost(self):
        for record in self:
            record.sub_cost = record.standard_price * record.product_qty


    @api.onchange('product_id')
    def onchange_product_id(self):
        self.size_panjang = self.product_id.size_panjang
        self.size_lebar = self.product_id.size_lebar
        self.size_tebal = self.product_id.size_tebal
        self.total_meter_cubic = self.product_id.total_meter_cubic
        self.total_meter_persegi = self.product_id.total_meter_persegi
        self.total_meter = self.product_id.total_meter
        self.description = self.product_id.description
        

    @api.onchange("kubikasi_id")
    def get_kubikasi(self):
        for tc in self:
            kbc = tc.kubikasi_id
            tc.size_tebal = kbc.size_tebal
            tc.size_panjang = kbc.size_panjang
            tc.size_lebar = kbc.size_lebar
            tc.total_meter_cubic = kbc.total_meter_cubic
            tc.total_meter_persegi = kbc.total_meter_persegi
            # tc.total_meter = kbc.total_meter

    # @api.depends("product_qty",'total_meter')
    # def get_calc(self):
    #     for record in self:
    #         record.total_meter = (record.total_meter1 * record.product_qty)

    @api.depends("product_qty",'total_meter')
    def get_calc_meter1(self):
        for record in self:
            record.total_meter1 = (record.total_meter * record.product_qty)

    @api.depends( "product_qty", "total_meter_cubic")
    def get_calc_mcubic1(self):
        for record in self:
            record.total_meter_cubic1 = (record.total_meter_cubic *  record.product_qty)

    @api.depends( "product_qty", "total_meter_persegi")
    def get_calc_mpersegi1(self):
        for record in self:
            record.total_meter_persegi1 = (record.total_meter_persegi *  record.product_qty)

    # @api.depends('size_panjang', 'size_lebar','size_tebal')
    # def get_calc(self):
    #     for cal in self:
    #         meter = cal.size_panjang * cal.size_lebar * cal.size_tebal
    #         cal.total_meter_cubic = ((meter) / 1000000000) * cal.product_qty if meter > 0 else 0.00
    #         cal.total_meter_persegi = ((meter) / 1000000) * cal.product_qty if meter > 0 else 0.00

    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_code = fields.Char('Code',store=True)
    design_detail_bom_line_ids = fields.One2many('mrp.bom.line', 'product_id',string='design_detail_bom_line')


class MrpWorkorderInherit(models.Model):
    _inherit = 'mrp.workorder'
    _description = 'mrp.workorder'

    balance = fields.Float('Balance',
        compute='_compute_balance' )
    
    @api.depends('qty_production','qty_producing')
    def _compute_balance(self):
        for r in self:
            r.balance = r.qty_production - r.qty_producing
    
    
    
    