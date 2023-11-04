from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError

class RndBoM(models.TransientModel):
    _name = "bom.rnd.wizard"
    _description = __doc__

    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id

    bom_id = fields.Many2one("mrp.bom","Bill Of Material")
    code = fields.Char('Reference')
    active = fields.Boolean(
        'Active', default=True,
        help="If the active field is set to False, it will allow you to hide the bills of material without removing it.")
    type = fields.Selection([
        ('normal', 'Manufacture this product'),
        ('phantom', 'Kit')], 'BoM Type',
        default='normal', required=True)
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product',
        check_company=True, index=True,
        domain="[('type', 'in', ['product', 'consu']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]", required=True)
    product_id = fields.Many2one(
        'product.product', 'Product Variant',
        check_company=True, index=True,
        domain="['&', ('product_tmpl_id', '=', product_tmpl_id), ('type', 'in', ['product', 'consu']),  '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If a product variant is defined the BOM is available only for this product.")
    bom_line_ids = fields.One2many('bom.rnd.wizard.line', 'bom_wizard_id', 'BoM Lines')
    byproduct_ids = fields.One2many('mrp.bom.byproduct.wizard', 'bom_wizard_id', 'By-products', copy=True)
    operation_ids = fields.One2many('mrp.routing.workcenter.wizard', 'bom_wizard_id', 'Operations')
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Unit of Measure', required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        default=_get_default_product_uom_id, required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control", domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_tmpl_id.uom_id.category_id')
    sequence = fields.Integer('Sequence', help="Gives the sequence order when displaying a list of bills of material.")
    ready_to_produce = fields.Selection([
        ('all_available', ' When all components are available'),
        ('asap', 'When components for 1st operation are available')], string='Manufacturing Readiness',
        default='asap', help="Defines when a Manufacturing Order is considered as ready to be started", required=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type', domain="[('code', '=', 'mrp_operation'), ('company_id', '=', company_id)]",
        check_company=True,
        help=u"When a procurement has a ‘produce’ route with a operation type set, it will try to create "
             "a Manufacturing Order for that product using a BoM of the same operation type. That allows "
             "to define stock rules which trigger different manufacturing orders with different BoMs.")
    company_id = fields.Many2one(
        'res.company', 'Company', index=True,
        default=lambda self: self.env.company)
    consumption = fields.Selection([
        ('flexible', 'Allowed'),
        ('warning', 'Allowed with warning'),
        ('strict', 'Blocked')],
        help="Defines if you can consume more or less components than the quantity defined on the BoM:\n"
             "  * Allowed: allowed for all manufacturing users.\n"
             "  * Allowed with warning: allowed for all manufacturing users with summary of consumption differences when closing the manufacturing order.\n"
             "  * Blocked: only a manager can close a manufacturing order when the BoM consumption is not respected.",
        default='warning',
        string='Flexible Consumption',
        required=True
    )
    is_product_componen = fields.Boolean("Is Product Componen", related='product_tmpl_id.is_componen')
    qty_so = fields.Integer("Quantity SO", compute="get_kubikasi", store=True,readonly=False)
    uom_so = fields.Many2one("uom.uom", "UoM SO", compute="get_kubikasi", store=True,readonly=False)
    size_tebal = fields.Float("Size Tebal", compute="get_kubikasi", store=True, readonly=False)
    size_lebar = fields.Float("Size Lebar", compute="get_kubikasi", store=True, readonly=False)
    size_panjang = fields.Float("Size Panjang", compute="get_kubikasi", store=True, readonly=False)
    total_meter_cubic = fields.Float("Meter Cubic (M³)", digits=(12, 8), compute="get_calc", store=True,readonly=False)
    total_meter_persegi = fields.Float("Meter Persegi (M²)", digits=(12, 8), compute="get_calc", store=True,readonly=False)
    ratio = fields.Integer("Rasio", compute="get_kubikasi", store=True,readonly=False)
    desc = fields.Char("Catatan", compute="get_kubikasi", store=True,readonly=False)

    @api.onchange("bom_id")
    def get_date_change(self):
        bom = self.bom_id
        if bom:
            self.sequence = bom.sequence
            self.product_tmpl_id = bom.product_tmpl_id.id
            self.product_id = bom.product_id.id
            self.code = bom.code
            self.type = bom.type
            self.company_id = bom.company_id.id
            self.ready_to_produce = bom.ready_to_produce
            self.picking_type_id = bom.picking_type_id.id
            self.consumption =  bom.consumption
            lines = []
            bom_line = bom
            operation = bom
            byproduct = bom
            for line in bom_line.bom_line_ids:
                lines.append((0,0,{
                        "product_id": line.product_id.id,
                        "product_tmpl_id": line.product_tmpl_id.id,
                        "product_qty": line.product_qty,
                        "operation_id": line.operation_id.id,
                    }))

            self.bom_line_ids = lines

            operation_ids = []
            for op in operation.operation_ids:
                operation_ids.append((0,0,{
                        "name": op.name,
                        "workcenter_id": op.workcenter_id.id,
                        "sequence": op.sequence,
                        "worksheet_type": op.worksheet_type,
                        "worksheet": op.worksheet,
                        "worksheet_google_slide": op.worksheet_google_slide,
                        "time_mode": op.time_mode,
                        "time_mode_batch": op.time_mode_batch,
                    }))

            self.operation_ids = operation_ids

            byproduct_ids = []
            for prod in byproduct.byproduct_ids:
                byproduct_ids.append((0,0,{
                        "product_id": prod.product_id.id,
                        "company_id": prod.company_id.id,
                        "product_qty": prod.product_qty,
                        "product_uom_id": prod.product_uom_id.id,
                        "operation_id": prod.operation_id.id,
                    }))

            self.byproduct_ids = byproduct_ids




    def action_confirm(self):
        bom = self.env['mrp.bom'].search([('id','=', self.bom_id.id)])
        bom_line_ids = []
        for line in self.bom_line_ids:
            bom_line_ids.append((0,0,{
                    "product_id": line.product_id.id,
                    "product_tmpl_id": line.product_tmpl_id.id,
                    "product_qty": line.product_qty,
                    "operation_id": line.operation_id.id,
                }))
        operation_ids = []
        for op in self.operation_ids:
            operation_ids.append((0,0,{
                    "name": op.name,
                    "workcenter_id": op.workcenter_id.id,
                    "sequence": op.sequence,
                    "worksheet_type": op.worksheet_type,
                    "worksheet": op.worksheet,
                    "worksheet_google_slide": op.worksheet_google_slide,
                    "time_mode": op.time_mode,
                    "time_mode_batch": op.time_mode_batch,
                }))
        byproduct_ids = []
        for prod in self.byproduct_ids:
            byproduct_ids.append((0,0,{
                    "product_id": prod.product_id.id,
                    "company_id": prod.company_id.id,
                    "product_qty": prod.product_qty,
                    "product_uom_id": prod.product_uom_id.id,
                }))
        obj = {
                'sequence' : self.sequence,
                'product_tmpl_id' : self.product_tmpl_id.id,
                'product_id' : self.product_id.id,
                'code' : self.code,
                'type' : self.type,
                'company_id' : self.company_id.id,
                'ready_to_produce' : self.ready_to_produce,
                'picking_type_id' : self.picking_type_id.id,
                'consumption' :  self.consumption,
                'bom_line_ids': bom_line_ids,
                'byproduct_ids': byproduct_ids,
                'operation_ids': operation_ids,
                'size_panjang': self.size_panjang,
                'size_lebar': self.size_lebar,
                'size_tebal': self.size_tebal,
                'total_meter_cubic': self.total_meter_cubic,
                'total_meter_persegi': self.total_meter_persegi,
                'ratio': self.ratio,
                'desc': self.desc,
                'qty_so': self.qty_so,
                'uom_so': self.uom_so,
        }
        bom.bom_line_ids.unlink()
        bom.byproduct_ids.unlink()
        bom.operation_ids.unlink()
        if bom:
            bom.write(obj)
        else:
            bom.create(obj)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }



    @api.depends("bom_id")
    def get_kubikasi(self):
        bom = self.bom_id
        self.size_tebal = bom.size_tebal
        self.size_panjang = bom.size_panjang
        self.size_lebar = bom.size_lebar
        self.ratio = bom.ratio
        self.desc = bom.desc
        self.uom_so = bom.uom_so.id
        self.qty_so = bom.qty_so

    @api.depends('size_panjang', 'size_lebar','size_tebal','qty_so','ratio')
    def get_calc(self):
        for cal in self:
            meter = cal.size_panjang * cal.size_lebar * cal.size_tebal
            total_meter_cubic = (meter) / 1000000000 if meter > 0 else 0.00
            total_meter_persegi = (meter) / 1000000 if meter > 0 else 0.00
            total_rasio = (cal.qty_so * cal.ratio)
            cal.total_meter_cubic = total_rasio * total_meter_cubic
            cal.total_meter_persegi = total_rasio * total_meter_persegi

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            for line in self.bom_line_ids:
                line.bom_product_template_attribute_value_ids = False

    @api.constrains('product_id', 'product_tmpl_id', 'bom_line_ids')
    def _check_bom_lines(self):
        for bom in self:
            for bom_line in bom.bom_line_ids:
                if bom.product_id:
                    same_product = bom.product_id == bom_line.product_id
                else:
                    same_product = bom.product_tmpl_id == bom_line.product_id.product_tmpl_id
                if same_product:
                    raise ValidationError(_("BoM line product %s should not be the same as BoM product.") % bom.display_name)
                if bom.product_id and bom_line.bom_product_template_attribute_value_ids:
                    raise ValidationError(_("BoM cannot concern product %s and have a line with attributes (%s) at the same time.")
                        % (bom.product_id.display_name, ", ".join([ptav.display_name for ptav in bom_line.bom_product_template_attribute_value_ids])))
                for ptav in bom_line.bom_product_template_attribute_value_ids:
                    if ptav.product_tmpl_id != bom.product_tmpl_id:
                        raise ValidationError(_(
                            "The attribute value %(attribute)s set on product %(product)s does not match the BoM product %(bom_product)s.",
                            attribute=ptav.display_name,
                            product=ptav.product_tmpl_id.display_name,
                            bom_product=bom_line.parent_product_tmpl_id.display_name
                        ))

    @api.onchange('product_uom_id')
    def onchange_product_uom_id(self):
        res = {}
        if not self.product_uom_id or not self.product_tmpl_id:
            return
        if self.product_uom_id.category_id.id != self.product_tmpl_id.uom_id.category_id.id:
            self.product_uom_id = self.product_tmpl_id.uom_id.id
            res['warning'] = {'title': _('Warning'), 'message': _('The Product Unit of Measure you chose has a different category than in the product form.')}
        return res

    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        if self.product_tmpl_id:
            self.product_uom_id = self.product_tmpl_id.uom_id.id
            if self.product_id.product_tmpl_id != self.product_tmpl_id:
                self.product_id = False
            for line in self.bom_line_ids:
                line.bom_product_template_attribute_value_ids = False

    def copy(self, default=None):
        res = super().copy(default)
        for bom_line in res.bom_line_ids:
            if bom_line.operation_id:
                operation = res.operation_ids.filtered(lambda op: op.name == bom_line.operation_id.name and op.workcenter_id == bom_line.operation_id.workcenter_id)
                bom_line.operation_id = operation
        return res

    @api.model
    def name_create(self, name):
        # prevent to use string as product_tmpl_id
        if isinstance(name, str):
            raise UserError(_("You cannot create a new Bill of Material from here."))
        return super(RndBoM, self).name_create(name)

    def name_get(self):
        return [(bom.id, '%s%s' % (bom.code and '%s: ' % bom.code or '', bom.product_tmpl_id.display_name)) for bom in self]

    @api.constrains('product_tmpl_id', 'product_id', 'type')
    def check_kit_has_not_orderpoint(self):
        product_ids = [pid for bom in self.filtered(lambda bom: bom.type == "phantom")
                           for pid in (bom.product_id.ids or bom.product_tmpl_id.product_variant_ids.ids)]
        if self.env['stock.warehouse.orderpoint'].search([('product_id', 'in', product_ids)], count=True):
            raise ValidationError(_("You can not create a kit-type bill of materials for products that have at least one reordering rule."))

    def unlink(self):
        if self.env['mrp.production'].search([('bom_id', 'in', self.ids), ('state', 'not in', ['done', 'cancel'])], limit=1):
            raise UserError(_('You can not delete a Bill of Material with running manufacturing orders.\nPlease close or cancel it first.'))
        return super(RndBoM, self).unlink()

    @api.model
    def _bom_find_domain(self, product_tmpl=None, product=None, picking_type=None, company_id=False, bom_type=False):
        if product:
            if not product_tmpl:
                product_tmpl = product.product_tmpl_id
            domain = ['|', ('product_id', '=', product.id), '&', ('product_id', '=', False), ('product_tmpl_id', '=', product_tmpl.id)]
        elif product_tmpl:
            domain = [('product_tmpl_id', '=', product_tmpl.id)]
        else:
            # neither product nor template, makes no sense to search
            raise UserError(_('You should provide either a product or a product template to search a BoM'))
        if picking_type:
            domain += ['|', ('picking_type_id', '=', picking_type.id), ('picking_type_id', '=', False)]
        if company_id or self.env.context.get('company_id'):
            domain = domain + ['|', ('company_id', '=', False), ('company_id', '=', company_id or self.env.context.get('company_id'))]
        if bom_type:
            domain += [('type', '=', bom_type)]
        # order to prioritize bom with product_id over the one without
        return domain

    @api.model
    def _bom_find(self, product_tmpl=None, product=None, picking_type=None, company_id=False, bom_type=False):
        """ Finds BoM for particular product, picking and company """
        if product and product.type == 'service' or product_tmpl and product_tmpl.type == 'service':
            return self.env['mrp.bom']
        domain = self._bom_find_domain(product_tmpl=product_tmpl, product=product, picking_type=picking_type, company_id=company_id, bom_type=bom_type)
        if domain is False:
            return self.env['mrp.bom']
        return self.search(domain, order='sequence, product_id', limit=1)

    @api.model
    def _get_product2bom(self, products, bom_type=False, picking_type=False, company_id=False):
        """Optimized variant of _bom_find to work with recordset"""

        bom_by_product = defaultdict(lambda: self.env['mrp.bom'])
        products = products.filtered(lambda p: p.type != 'service')
        if not products:
            return bom_by_product
        product_templates = products.mapped('product_tmpl_id')
        domain = ['|', ('product_id', 'in', products.ids), '&', ('product_id', '=', False), ('product_tmpl_id', 'in', product_templates.ids)]
        if picking_type:
            domain += ['|', ('picking_type_id', '=', picking_type.id), ('picking_type_id', '=', False)]
        if company_id or self.env.context.get('company_id'):
            domain = domain + ['|', ('company_id', '=', False), ('company_id', '=', company_id or self.env.context.get('company_id'))]
        if bom_type:
            domain += [('type', '=', bom_type)]

        if len(products) == 1:
            bom = self.search(domain, order='sequence, product_id, id', limit=1)
            if bom:
                bom_by_product[products] = bom
            return bom_by_product

        boms = self.search(domain, order='sequence, product_id, id')

        products_ids = set(products.ids)
        for bom in boms:
            products_implies = bom.product_id or bom.product_tmpl_id.product_variant_ids
            for product in products_implies:
                if product.id in products_ids and product not in bom_by_product:
                    bom_by_product[product] = bom
        return bom_by_product

    def explode(self, product, quantity, picking_type=False):
        """
            Explodes the BoM and creates two lists with all the information you need: bom_done and line_done
            Quantity describes the number of times you need the BoM: so the quantity divided by the number created by the BoM
            and converted into its UoM
        """
        from collections import defaultdict

        graph = defaultdict(list)
        V = set()

        def check_cycle(v, visited, recStack, graph):
            visited[v] = True
            recStack[v] = True
            for neighbour in graph[v]:
                if visited[neighbour] == False:
                    if check_cycle(neighbour, visited, recStack, graph) == True:
                        return True
                elif recStack[neighbour] == True:
                    return True
            recStack[v] = False
            return False

        product_ids = set()
        product_boms = {}
        def update_product_boms():
            products = self.env['product.product'].browse(product_ids)
            product_boms.update(self._get_product2bom(products, bom_type='phantom',
                picking_type=picking_type or self.picking_type_id, company_id=self.company_id.id))
            # Set missing keys to default value
            for product in products:
                product_boms.setdefault(product, self.env['mrp.bom'])

        boms_done = [(self, {'qty': quantity, 'product': product, 'original_qty': quantity, 'parent_line': False})]
        lines_done = []
        V |= set([product.product_tmpl_id.id])

        bom_lines = []
        for bom_line in self.bom_line_ids:
            product_id = bom_line.product_id
            V |= set([product_id.product_tmpl_id.id])
            graph[product.product_tmpl_id.id].append(product_id.product_tmpl_id.id)
            bom_lines.append((bom_line, product, quantity, False))
            product_ids.add(product_id.id)
        update_product_boms()
        product_ids.clear()
        while bom_lines:
            current_line, current_product, current_qty, parent_line = bom_lines[0]
            bom_lines = bom_lines[1:]

            if current_line._skip_bom_line(current_product):
                continue

            line_quantity = current_qty * current_line.product_qty
            if not current_line.product_id in product_boms:
                update_product_boms()
                product_ids.clear()
            bom = product_boms.get(current_line.product_id)
            if bom:
                converted_line_quantity = current_line.product_uom_id._compute_quantity(line_quantity / bom.product_qty, bom.product_uom_id)
                bom_lines += [(line, current_line.product_id, converted_line_quantity, current_line) for line in bom.bom_line_ids]
                for bom_line in bom.bom_line_ids:
                    graph[current_line.product_id.product_tmpl_id.id].append(bom_line.product_id.product_tmpl_id.id)
                    if bom_line.product_id.product_tmpl_id.id in V and check_cycle(bom_line.product_id.product_tmpl_id.id, {key: False for  key in V}, {key: False for  key in V}, graph):
                        raise UserError(_('Recursion error!  A product with a Bill of Material should not have itself in its BoM or child BoMs!'))
                    V |= set([bom_line.product_id.product_tmpl_id.id])
                    if not bom_line.product_id in product_boms:
                        product_ids.add(bom_line.product_id.id)
                boms_done.append((bom, {'qty': converted_line_quantity, 'product': current_product, 'original_qty': quantity, 'parent_line': current_line}))
            else:
                # We round up here because the user expects that if he has to consume a little more, the whole UOM unit
                # should be consumed.
                rounding = current_line.product_uom_id.rounding
                line_quantity = float_round(line_quantity, precision_rounding=rounding, rounding_method='UP')
                lines_done.append((current_line, {'qty': line_quantity, 'product': current_product, 'original_qty': quantity, 'parent_line': parent_line}))

        return boms_done, lines_done







class RnDMrpBomLine(models. TransientModel):
    _name = "bom.rnd.wizard.line"
    _order = "sequence, id"
    _rec_name = "product_id"
    _description = 'Bill of Material Line'
    _check_company_auto = True



    bom_wizard_id = fields.Many2one(
        'bom.rnd.wizard', 'Parent BoM', required=True)


    def _get_default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id').id


    product_id = fields.Many2one('product.product', 'Component', required=True, check_company=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id')
    company_id = fields.Many2one(
        related='bom_wizard_id.company_id', store=True, index=True, readonly=True)
    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        default=_get_default_product_uom_id,
        required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control", domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    sequence = fields.Integer(
        'Sequence', default=1,
        help="Gives the sequence order when displaying.")
    parent_product_tmpl_id = fields.Many2one('product.template', 'Parent Product Template', related='bom_wizard_id.product_tmpl_id')
    bom_product_template_attribute_value_ids = fields.Many2many(
        'product.template.attribute.value', string="Apply on Variants", ondelete='restrict',
        domain="[('id', 'in', possible_bom_product_template_attribute_value_ids)]",
        help="BOM Product Variants needed to apply this line.")
    operation_id = fields.Many2one(
        'mrp.routing.workcenter', 'Consumed in Operation', check_company=True,
        help="The operation where the components are consumed, or the finished products created.")


    def action_see_attachments(self):
        domain = [
            '|',
            '&', ('res_model', '=', 'product.product'), ('res_id', '=', self.product_id.id),
            '&', ('res_model', '=', 'product.template'), ('res_id', '=', self.product_id.product_tmpl_id.id)]
        attachment_view = self.env.ref('mrp.view_document_file_kanban_mrp')
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'mrp.document',
            'type': 'ir.actions.act_window',
            'view_id': attachment_view.id,
            'views': [(attachment_view.id, 'kanban'), (False, 'form')],
            'view_mode': 'kanban,tree,form',
            'help': _('''<p class="o_view_nocontent_smiling_face">
                        Upload files to your product
                    </p><p>
                        Use this feature to store any files, like drawings or specifications.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d, 'default_company_id': %s}" % ('product.product', self.product_id.id, self.company_id.id)
        }






class MrpRoutingWorkcenterWizaed(models. TransientModel):
    _name = 'mrp.routing.workcenter.wizard'
    _description = 'Work Center Usage'
    _order = 'sequence, id'
    _check_company_auto = True





    name = fields.Char('Operation', required=True)
    workcenter_id = fields.Many2one('mrp.workcenter', 'Work Center', required=True, check_company=True)
    sequence = fields.Integer(
        'Sequence', default=100,
        help="Gives the sequence order when displaying a list of routing Work Centers.")
    bom_wizard_id = fields.Many2one(
        'bom.rnd.wizard', 'Parent BoM',
        index=True, ondelete='cascade', required=True)

    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company)
    worksheet_type = fields.Selection([
        ('pdf', 'PDF'), ('google_slide', 'Google Slide'), ('text', 'Text')],
        string="Work Sheet", default="text",
        help="Defines if you want to use a PDF or a Google Slide as work sheet."
    )
    note = fields.Text('Description', help="Text worksheet description")
    worksheet = fields.Binary('PDF')
    worksheet_google_slide = fields.Char('Google Slide', help="Paste the url of your Google Slide. Make sure the access to the document is public.")
    time_mode = fields.Selection([
        ('auto', 'Compute based on tracked time'),
        ('manual', 'Set duration manually')], string='Duration Computation',
        default='manual')
    time_mode_batch = fields.Integer('Based on', default=10)
    time_cycle_manual = fields.Float(
        'Manual Duration', default=60,
        help="Time in minutes:"
        "- In manual mode, time used"
        "- In automatic mode, supposed first time when there aren't any work orders yet")
    time_cycle = fields.Float('Duration', compute="_compute_time_cycle")
    workorder_count = fields.Integer("# Work Orders", compute="_compute_workorder_count")
    workorder_ids = fields.One2many('mrp.workorder', 'operation_id', string="Work Orders")

    @api.depends('time_cycle_manual', 'time_mode', 'workorder_ids')
    def _compute_time_cycle(self):
        manual_ops = self.filtered(lambda operation: operation.time_mode == 'manual')
        for operation in manual_ops:
            operation.time_cycle = operation.time_cycle_manual
        for operation in self - manual_ops:
            data = self.env['mrp.workorder'].search([
                ('operation_id', '=', operation.id),
                ('qty_produced', '>', 0),
                ('state', '=', 'done')],
                limit=operation.time_mode_batch,
                order="date_finished desc")
            # To compute the time_cycle, we can take the total duration of previous operations
            # but for the quantity, we will take in consideration the qty_produced like if the capacity was 1.
            # So producing 50 in 00:10 with capacity 2, for the time_cycle, we assume it is 25 in 00:10
            # When recomputing the expected duration, the capacity is used again to divide the qty to produce
            # so that if we need 50 with capacity 2, it will compute the expected of 25 which is 00:10
            total_duration = 0  # Can be 0 since it's not an invalid duration for BoM
            cycle_number = 0  # Never 0 unless infinite item['workcenter_id'].capacity
            for item in data:
                total_duration += item['duration']
                cycle_number += tools.float_round((item['qty_produced'] / item['workcenter_id'].capacity or 1.0), precision_digits=0, rounding_method='UP')
            if cycle_number:
                operation.time_cycle = total_duration / cycle_number
            else:
                operation.time_cycle = operation.time_cycle_manual

    def _compute_workorder_count(self):
        data = self.env['mrp.workorder'].read_group([
            ('operation_id', 'in', self.ids),
            ('state', '=', 'done')], ['operation_id'], ['operation_id'])
        count_data = dict((item['operation_id'][0], item['operation_id_count']) for item in data)
        for operation in self:
            operation.workorder_count = count_data.get(operation.id, 0)





class MrpByProductWizard(models. TransientModel):
    _name = 'mrp.bom.byproduct.wizard'
    _description = 'Byproduct'
    _rec_name = "product_id"
    _check_company_auto = True



    product_id = fields.Many2one('product.product', 'By-product', required=True, check_company=True)
    company_id = fields.Many2one(related='bom_wizard_id.company_id', store=True, index=True, readonly=True)
    product_qty = fields.Float(
        'Quantity',
        default=1.0, digits='Product Unit of Measure', required=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    bom_wizard_id = fields.Many2one(
        'bom.rnd.wizard', 'Parent BoM',
        index=True, ondelete='cascade', required=True)
    operation_id = fields.Many2one(
        'mrp.routing.workcenter', 'Produced in Operation')



    @api.onchange('product_id')
    def onchange_product_id(self):
        """ Changes UoM if product_id changes. """
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id

    @api.onchange('product_uom_id')
    def onchange_uom(self):
        res = {}
        if self.product_uom_id and self.product_id and self.product_uom_id.category_id != self.product_id.uom_id.category_id:
            res['warning'] = {
                'title': _('Warning'),
                'message': _('The unit of measure you choose is in a different category than the product unit of measure.')
            }
            self.product_uom_id = self.product_id.uom_id.id
        return res
