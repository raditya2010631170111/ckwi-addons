# -*- coding: utf-8 -*-
from odoo import _, models, fields, api

class ResWoodClass(models.Model):
    _name = 'res.wood.class'
    _description = 'Res Wood Class'
    
    name = fields.Char('Kelas')


class ResCertification(models.Model):
    _name = 'res.certification'
    _description = 'Resource Certification'

    name = fields.Char(string='Certification') 


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    code = fields.Char('Code')
    snp_id = fields.Char('SNP')
    wood_type = fields.Selection([
        ('log', 'LOG'),
        ('square', 'Square Log'),
        ('timber', 'Sawn Timber')
    ], string='Type')
    wood_kind_id = fields.Many2one(comodel_name='jidoka.woodkind', string='Jenis Kayu')
    wood_class_id = fields.Many2one('res.wood.class', string='Wood Class')
    certification_id = fields.Many2one('res.certification',string='Sertifikasi')
    model = fields.Char('Model', store=True)
    is_jati = fields.Boolean('Is Jati?')
    is_prod_brg_jadi = fields.Boolean('Is Barang Jadi?', default= False)
    wood_grade_id = fields.Many2one('wood.grade', string='Grade')
    wood_shape_id = fields.Many2one('jidoka.woodshape', string='Bentuk')
    colour_id = fields.Many2one('res.fabric.colour', string='Warna')
    wood_ok = fields.Boolean('Show PCS', default = False,)
    is_show_pcs = fields.Boolean('Show PCS', default = False, )
    count_wood = fields.Integer('Count Serial')
    count_show_tmpl = fields.Integer('Count Show Pcs', 
        compute='_compute_count_show_tmpl')
    product_template_attribute_value_ids = fields.Many2many('product.template.attribute.value', 
        string='Product Template Atribute', 
        related='product_variant_ids.product_template_attribute_value_ids')
    tebal = fields.Float(string='Tebal (cm)',
    readonly= False, compute= '_onchange_tebal')
    size_tebal = fields.Float("Size Tebal",)
    net_weight = fields.Float('Net Weight', store=True)
    gross_weight = fields.Float('Gross Weight', store=True)
    pack = fields.Float('Pack', store=True)
    means = fields.Float('Means', store=True)
    is_kayu = fields.Boolean('Is Kayu', compute='_compute_is_kayu',store=True )
    
    @api.depends('wood_type')
    def _compute_is_kayu(self):
        for r in self:
            if r.wood_type == False:
                r.is_kayu = False
            else:
                r.is_kayu = True

    @api.onchange('size_tebal')
    def _onchange_tebal(self):
        self.tebal = self.size_tebal

    @api.depends(
            'product_variant_ids',
            'product_variant_ids.stock_move_ids.product_qty',
            'product_variant_ids.stock_move_ids.state',
        )    
    def _compute_count_show_tmpl(self):
        for r in self:
            stock_quants = self.env['stock.quant'].search_count([
                ('product_id','in', r.product_variant_ids.ids),
                ('on_hand','=',True)])
            r.count_show_tmpl = stock_quants
                
    # Be aware that the exact same function exists in product.product
    def action_open_quants_tmpl(self):
        return self.product_variant_ids.filtered(lambda p: p.active or p.qty_available != 0).action_open_quants_pr()
    

    
class ProductProductKubik(models.Model):
    _inherit = 'product.product'
    
    stock_quant_ids = fields.One2many('stock.quant', 'product_id', string='stock_quant')
    wood_ok = fields.Boolean('Show PCS', default = False)
    count_show_pr = fields.Integer('Count Show Pcs', compute='_compute_count_show_pr')
    is_prod_brg_jadi = fields.Boolean('Is Barang Jadi?', default= False)
    is_kayu = fields.Boolean('Is Kayu', compute='_compute_is_kayu', store=True )
    
    @api.depends('wood_type')
    def _compute_is_kayu(self):
        for r in self:
            if r.wood_type == False:
                r.is_kayu = False
            else:
                r.is_kayu = True
    
    @api.depends(
        'stock_move_ids.product_qty',
        'stock_move_ids.state',
        )    
    def _compute_count_show_pr(self):
        for r in self:
            stock_quants = self.env['stock.quant'].search_count([
                ('product_id','=', r.id),
                ('on_hand','=',True)])
            r.count_show_pr = stock_quants
    
    def action_open_quants_m3(self):
        return self.product_variant_ids.filtered(lambda p: p.active or p.qty_available != 0).action_open_quants_m3()
    
    def action_open_quants_tmpl(self):
        return self.product_variant_ids.filtered(lambda p: p.active or p.qty_available != 0).action_open_quants_pr()
     
    # Be aware that the exact same function exists in product.template
    def action_open_quants_pr(self):
        domain = [('product_id', 'in', self.ids)]
        hide_location = not self.user_has_groups('stock.group_stock_multi_locations')
        hide_lot = all(product.tracking == 'none' for product in self)
        self = self.with_context(
            hide_location=hide_location, hide_lot=hide_lot,
            no_at_date=True, search_default_on_hand=True,
        )

        # If user have rights to write on quant, we define the view as editable.
        if self.user_has_groups('stock.group_stock_manager'):
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.user_has_groups('stock.group_stock_multi_locations'):
                user_company = self.env.company
                warehouse = self.env['stock.warehouse'].search(
                    [('company_id', '=', user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(default_location_id=warehouse.lot_stock_id.id)
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(
                default_product_id=self.id,
                single_product=True
            )
        else:
            self = self.with_context(product_tmpl_ids=self.product_tmpl_id.ids)
        action = self.env['stock.quant']._get_quants_m3_action(domain)
        action["name"] = _('Update Quantity Unit')
        return action


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    standard_price = fields.Float(related='product_id.standard_price', string="Cost", store=True )
                
    
    @api.model
    def _get_quants_m3_action(self, domain=None, extend=False):
        """ Returns an action to open quant view.
        Depending of the context (user have right to be inventory mode or not),
        the list view will be editable or readonly.

        :param domain: List for the domain, empty by default.
        :param extend: If True, enables form, graph and pivot views. False by default.
        """
        if not self.env['ir.config_parameter'].sudo().get_param('stock.skip_quant_tasks'):
            self._quant_tasks()
        ctx = dict(self.env.context or {})
        ctx.pop('group_by', None)
        action = {
            'name': _('Update Quantity Unit'),
            # 'view_type': 'tree',
            'view_type': 'tree',
            'view_mode': 'tree,list,form',
            'res_model': 'stock.quant',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': domain or [],
            'help': """
                <p class="o_view_nocontent_empty_folder">No Stock On Hand</p>
                <p>This analysis gives you an overview of the current stock
                level of your products.</p>
                """
        }

        target_action = self.env.ref('stock.dashboard_open_quants', False)
        if target_action:
            action['id'] = target_action.id

        if self._is_inventory_mode():
            action['view_id'] = self.env.ref('jidoka_inventory.view_stock_quant_tree_inherit_editable').id            
            form_view = self.env.ref('stock.view_stock_quant_form_editable').id
        else:
            action['view_id'] = self.env.ref('stock.view_stock_quant_tree').id
            form_view = self.env.ref('stock.view_stock_quant_form').id
        action.update({
            'views': [
                (action['view_id'], 'list'),
                (form_view, 'form'),
            ],
        })
        if extend:
            action.update({
                'view_mode': 'tree,form,pivot,graph',
                'views': [
                    (action['view_id'], 'list'),
                    (form_view, 'form'),
                    (self.env.ref('stock.view_stock_quant_pivot').id, 'pivot'),
                    (self.env.ref('stock.stock_quant_view_graph').id, 'graph'),
                ],
            })
        return action
    

class ProductWoodKind(models.Model):
    _name = 'jidoka.woodkind'
    _description = 'Wood Kind (Jenis Kayu)'
    
    name = fields.Char(string='Name', required=True)


class KeteranganMasalah(models.Model):
    _name = 'jidoka.ketmasalah'
    _description = 'Defect'
    
    name = fields.Char('Code', required=True)  
    description_ids = fields.Many2many('jidoka.isi.defect', string='Description')

class KeteranganMasalah(models.Model):
    _name = 'jidoka.isi.defect'
    _description = 'Defect'
    
    name = fields.Text('Isi Defect', required=True)  
    category = fields.Many2one('jidoka.category.defect', string='Category Defect', required=True)

class KeteranganMasalah(models.Model):
    _name = 'jidoka.category.defect'
    _description = 'Category Defect'
    
    name = fields.Text('Category Defect', required=True)  

class Species(models.Model):
    _name = 'jidoka.species'
    _description = 'Species'
    
    name = fields.Char('Name', required=True)  
     
class WoodShape(models.Model):
    _name = 'jidoka.woodshape'
    _description = 'Bentuk Kayu'

    name = fields.Char('Bentuk', required=True)
    description = fields.Char('Description')

class WoodGrade(models.Model):
    _name = 'wood.grade'
    _description = 'Master Data Wood Grading'

    name = fields.Char('Grade')
    description = fields.Char('Description')


