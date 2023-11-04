from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import ValidationError, UserError


import logging
_logger = logging.getLogger(__name__)


class DesignProcess(models.Model):
    _inherit = 'design.process'

    design_detail_ids = fields.One2many('design.detail', 'design_process_id', string='Design Detail')

    def create_design_detail(self):
        for rec in self:
            vals = [(5,0)]
            for spec in rec.spec_design_ids:
                vals.append((0,0,{
                    'spec_design_id': spec.id
                }))
            rec.design_detail_ids = vals
            
    

    # def create_design_detail(self):
    #     for rec in self:
    #         # Dapatkan crm.lead yang ingin Anda tambahkan design_detail_ids-nya
    #         lead = self.env['crm.lead'].browse(lead_id)
            
    #         # Buat design.detail baru dari spec_design_ids
    #         design_details = []
    #         for spec in rec.spec_design_ids:
    #             design_details.append((0, 0, {'spec_design_id': spec.id}))
            
    #         # Gabungkan design_details dengan design_detail_ids yang sudah ada
    #         design_detail_ids = lead.design_detail_ids + design_details
            
    #         # Atur nilai design_detail_ids pada crm.lead yang sudah diambil sebelumnya
    #         lead.write({'design_detail_ids': design_detail_ids})
    
    def action_validate(self):
        return {
                'name' : _("Validate With Comment"),
                'view_type' : 'form',
                'res_model' : 'approval.history.rnd.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
            }

    def validate_design(self):
        BOM = self.env['mrp.bom']
        bom_line_ids = []
        if self.is_set and self.item:
            obj = {
                'product_tmpl_id': self.item.product_tmpl_id.id,
                'product_qty': 1,
                'product_uom_id': self.item.uom_id.id,
                'code': self.name,
                'rnd_id': self.id,
                'crm_id': self.crm_id.id
            }
            for rec in self.design_detail_ids.filtered(lambda r:r.state == 'confirm'):
                bom_line_ids.append((0,0,{
                    'product_id':rec.product_id.id,
                    'product_uom_id':rec.product_id.uom_id.id,
                    # 'size_panjang':rec.size_panjang,
                    # 'size_lebar':rec.size_lebar,
                    # 'size_tebal':rec.size_tebal,
                    # 'total_meter_cubic':rec.total_meter_cubic,
                    # 'total_meter_persegi':rec.total_meter_persegi
                }))
            obj['bom_line_ids'] = bom_line_ids
            bom_id = BOM.create(obj)
            bom_id.onchange_product_id()
            bom_id._check_bom_lines()
            bom_id.onchange_product_uom_id()
            bom_id.onchange_product_tmpl_id()
            bom_id.check_kit_has_not_orderpoint()
            

class DesignDetail(models.Model):
    _name = 'design.detail'
    _description = 'Design Detail'
    
    request_no = fields.Char("No. Spec Design",related='spec_design_id.request_no')
    
    detail_material_ids = fields.Many2many('design.material', 'design_detail_material_rel', 'detail_id', 'material_id', string='Material', related='design_process_id.detail_material_ids')
    detail_finish_ids = fields.Many2many('design.finish', 'design_detail_finish_rel', 'detail_id', 'material_id', string='Finish', related='design_process_id.detail_finish_ids')

    name = fields.Char('Reference',
        required=True, copy=False,
        index='trigram',
        states={'Done': [('readonly', True)]},
        default=lambda self: _('New'))
    sub_cost = fields.Float('Subtotal Cost',digits='Product Unit of Measure' ,store=True,)
    design_process_id = fields.Many2one('design.process', string='Design Process')
    spec_design_id = fields.Many2one('spec.design', string='Spec Design')
    product_id = fields.Many2one('product.product', related='spec_design_id.item_id',string='Spec. Design Item',store=True)
    crm_id = fields.Many2one("crm.lead",related='spec_design_id.crm_id',string="CRM",store=True)
    design_buyer_attach = fields.Image('Design Buyer', max_width=512, max_height=512, store=True,
    related='spec_design_id.attachment')
    design_done_attach = fields.Image('Design Done', max_width=512, max_height=512, store=True,
    )
    design_detail_date = fields.Date('Design Detail Created Date',default=fields.Date.context_today)

    is_bom_created = fields.Boolean(string='BOM Created',default=False)
    is_action_costing = fields.Boolean(string='Costing Created',default=False)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('processing', 'Processing'),
        ('to_review', 'To Review'),
        ('marketing_review', 'Marketing Review'),
        ('in_review', 'Assign Buyer'),
        ('confirm', 'Confirmed'),
        ('need_revised', 'Need Revised'),
        ('revised', 'Revised')
    ], string='State',default='draft')
    # is_need_revision = fields.Boolean('Is Need Revision',default=False)
    feedback_date = fields.Date('Feedback Date')
    feedback_notes = fields.Text('Feedback Notes')
    # code = fields.Char(string='code', related='state.code', store=True)
    # state_type = fields.Char("State Type", related="state.code", store=True)

    verifikasi_design = fields.One2many("verifikasi.design","design_detail_id", string="Verifikasi Design", 
        max_width=512, max_height=512, copy=True, store=True)

    sket_warna = fields.One2many("sket.warna","design_detail_id", string="Sket Warna",
        max_width=512, max_height=512, copy=True, store=True)

    explode_diagram = fields.One2many("explode.diagram","design_detail_id", string="Explode Diagram", 
        max_width=512, max_height=512, copy=True, store=True)

    sket_detail = fields.One2many("sket.detail","design_detail_id", string="Sket Detail", 
        max_width=512, max_height=512, copy=True, store=True)
    component_line_ids = fields.One2many('design.detail.bom.line', 'design_detail_id', string='Component', copy=True, store=True )
    hardware_line_ids = fields.One2many('design.detail.hardware', 'design_detail_id', string='Hardware', copy=True, store=True)
    special_material_line_ids = fields.One2many('design.detail.special.material', 'design_detail_id', string='Special Material', copy=True, store=True)
    operation_ids = fields.One2many('mrp.routing.workcenter', 'design_detail_id', string='Bom Operations', copy=True, store=True)
    bom_id = fields.Many2one('mrp.bom', string='BoM')
    origin_id = fields.Many2one('design.detail', string='Origin')
    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    count_costing = fields.Integer("Costing Count", compute="compute_count_costing")

    @api.depends('request_no')
    def compute_count_costing(self):
        for detail in self:
            count = self.env['summary.costing'].search_count([('request_no', '=', detail.request_no)])
            detail.count_costing = count
    

    def get_costing_bom(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Summary Costing',
            'view_mode': 'tree,form',
            'res_model': 'summary.costing',
            'domain': [('request_no', '=', self.request_no)],
            'context': "{'create': False}"
        }
    

    def name_get(self):
        if self._context.get('display_product'):
            res = []
            for record in self:
                # product_id = record.parent.design_detail_ids.filtered(lambda l: l.state == 'marketing_review')
                name = record.name
                if record.product_id:
                    name = record.product_id.display_name
                res.append((record.id, name))
            return res
        else:
            return super(DesignDetail, self).name_get()
        

    def action_costing(self):
        for res in self:

            # inisialisasi dictionary kosong untuk menyimpan recordset
            lines_dict = {}

            # loop pada masing-masing recordset dan masukkan ke dalam dictionary sesuai product_id
            for line in res.component_line_ids:
                if line.product_id.id not in lines_dict:
                    lines_dict[line.product_id.id] = [line]
                else:
                    lines_dict[line.product_id.id].append(line)

            for line in res.hardware_line_ids:
                if line.product_id.id not in lines_dict:
                    lines_dict[line.product_id.id] = [line]
                else:
                    lines_dict[line.product_id.id].append(line)

            for line in res.special_material_line_ids:
                if line.product_id.id not in lines_dict:
                    lines_dict[line.product_id.id] = [line]
                else:
                    lines_dict[line.product_id.id].append(line)

            # loop pada dictionary dan gabungkan informasi yang dibutuhkan dari recordset yang berbeda
            actual_cost = []
            for product_id, lines in lines_dict.items():
                for line in lines:
                    actual_cost.append((0, 0, {
                        'product_id': product_id,
                        # tambahkan bidang lain yang diperlukan
                    }))

            wood_cost = []
            for line in res.component_line_ids:
                wood_cost.append((0,0,{
                        'product_id' : line.product_id.id,
                        'qty' : line.product_qty,
                        'component_size_t' : line.size_tebal,
                        'component_size_p' : line.size_panjang,
                        'component_size_l' : line.size_lebar,
                        'price_currency' : line.standard_price,
                        }))
                
            hardware_cost = []
            for line in res.hardware_line_ids:
                hardware_cost.append((0,0,{
                        'product_id' : line.product_id.id,
                        'qty' : line.product_qty,
                        'price_currency': line.standard_price, 
                        }))
                
            special_cost = []
            for line in res.special_material_line_ids:
                special_cost.append((0,0,{
                        'product_id' : line.product_id.id,
                        'qty' : line.product_qty,
                        'price_currency': line.standard_price, 
                        }))

                cost_vals = {
                        'item_id': self.product_id.id,
                        'item_no': self.product_id.id,
                        'request_no' : self.request_no,
                        'detail_material_ids': self.detail_material_ids.ids,
                        'detail_finish_ids' : self.detail_finish_ids.ids,
                        'wood_costing_line_ids' : wood_cost,
                        'hadware_costing_line_ids' : hardware_cost,
                        'spesials_material_costing_line_ids' : special_cost,
                        'actual_costing_line_ids' : actual_cost,
                }
                self.is_action_costing = True
                self.write({'is_action_costing': True})

                cost = self.env['summary.costing']
                cost.create(cost_vals)



    # def create_revise_document(self):
    #     for rec in self:
    #         rec.copy({'name':self.name + ' (Revised)','state':'draft','origin_id':self.id})
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'reload',         
    #  }

    def create_revise_document(self):
        for rec in self:
            rec.copy({'name':self.name + ' (Revised)','state':'draft','origin_id':self.id})
            for r in self:
                    r.state = 'revised'
            return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',         
     }
        

    # def create_revise_document(self):
    #     for rec in self:
    #         rec.copy({'name': self.name + ' (Revised)', 'state': 'draft', 'origin_id': self.id})
    #         for r in rec:
    #             r.state = 'revised'
    #             for line in r.component_line_ids:
    #                 if line.type != 'product':
    #                     raise ValidationError('Quants cannot be created for consumables or services.')
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'reload',
    #         }


    def _create_bom(self, parent_product_id, create_component=None,component_ids=None,hardware_ids=None,special_material_ids=None):
        BOM = self.env['mrp.bom']
        bom_line_ids = []
        obj = {
            'product_tmpl_id': parent_product_id.product_tmpl_id.id,
            'product_qty': 1,
            'product_uom_id': parent_product_id.uom_id.id,
            'code': self.name,
            'rnd_id': self.design_process_id.id,
            'crm_id': self.design_process_id.crm_id.id
        }
        if create_component :
            for rec in component_ids:
                bom_line_ids.append((0,0,{
                    'product_id':rec.product_id.id,
                    'product_uom_id':rec.product_uom_id.id,
                    'size_panjang':rec.size_panjang,
                    'size_lebar':rec.size_lebar,
                    'size_tebal':rec.size_tebal,
                    'total_meter_cubic':rec.total_meter_cubic,
                    'total_meter_persegi':rec.total_meter_persegi,
                    'product_qty' : rec.product_qty,
                    'product_code' : rec.product_code,
                    'description' : rec.description,
                    'standard_price': rec.standard_price,
                    'sub_cost': rec.sub_cost,
                    
                }))
            for rec in hardware_ids:
                bom_line_ids.append((0,0,{ 
                    'product_id':rec.product_id.id,
                    'product_qty' : rec.product_qty,
                    'description' : rec.description,
                    'standard_price': rec.standard_price,
                   
                }))
            for rec in special_material_ids:
                bom_line_ids.append((0,0,{ 
                    'product_id':rec.product_id.id,
                    'product_qty' : rec.product_qty,
                    'description' : rec.description,
                    'standard_price': rec.standard_price,
                    
                }))

            obj['bom_line_ids'] = bom_line_ids
        bom_id = BOM.create(obj)
        bom_id.onchange_product_id()
        bom_id._check_bom_lines()
        bom_id.onchange_product_uom_id()
        bom_id.onchange_product_tmpl_id()
        bom_id.check_kit_has_not_orderpoint()
        return bom_id

    def _create_product_component(self):
        # Create product from component
        for rec in self.component_line_ids.filtered(lambda r: not r.product_tmpl_id):
            vals = {
                'product_code':rec.product_code,
                'name':rec.component,
                'is_componen':True,
                'type':rec.type,
                'categ_id':rec.categ_id.id,
                'uom_id':rec.product_uom_id.id,
                'rasio':rec.rasio,
                'model':rec.model,
                'size_panjang':rec.size_panjang,
                'size_lebar':rec.size_lebar,
                'size_tebal':rec.size_tebal,
                'total_meter_cubic':rec.total_meter_cubic,
                'total_meter_persegi':rec.total_meter_persegi,
                'standard_price': rec.standard_price,

                
            }
            if rec.sale_ok:
                vals['sale_ok'] = True 
            else:
                vals['sale_ok'] = False  
         
            if rec.purchase_ok:
                vals['purchase_ok'] = True 
            else:
                vals['purchase_ok'] = False 

          

            if rec.is_manufacture:
                vals['route_ids'] = [(4, 5), (3, 7)]
                # vals['route_ids'] = [(4, self.env.ref('mrp.route_warehouse0_manufacture').id), (3, self.env.ref('mrp.route_warehouse0_manufacture').id)]
            product_tmpl_id = self.env['product.template'].create(vals)
            rec.product_tmpl_id = product_tmpl_id.id
            rec.product_id = product_tmpl_id.product_variant_ids.ids[0]
            if rec.is_manufacture:
                self._create_bom(self.env['product.product'].browse(product_tmpl_id.product_variant_ids.ids[0]))
           
                 


    def create_bom_document(self):
        self.is_bom_created = True
    
        vals = []
        self._create_product_component()
        #create bom
        # bom = self.env['mrp.bom'].search([('product_tmpl_id','=', self.product_id.product_tmpl_id.id)])
        bom_id = self._create_bom(parent_product_id=self.product_id, create_component=True, component_ids=self.component_line_ids, hardware_ids=self.hardware_line_ids,special_material_ids=self.special_material_line_ids.filtered(lambda r:r.product_id))
        # BOM = self.env['mrp.bom']
        # bom_line_ids = []
        # for rec in self.component_line_ids.filtered(lambda r:r.product_id):
        #     bom_line_ids.append((0,0,{
        #         'product_id':rec.product_id.id,
        #         'product_uom_id':rec.product_uom_id.id,
        #         'size_panjang':rec.size_panjang,
        #         'size_lebar':rec.size_lebar,
        #         'size_tebal':rec.size_tebal,
        #         'total_meter_cubic':rec.total_meter_cubic,
        #         'total_meter_persegi':rec.total_meter_persegi
        #     }))
        # obj = {
        #     'product_tmpl_id': self.product_id.product_tmpl_id.id,
        #     'product_qty': 1,
        #     'product_uom_id': self.product_id.uom_id.id,
        #     'code': self.name,
        #     'rnd_id': self.design_process_id.id,
        #     'crm_id': self.design_process_id.crm_id.id,
        #     'bom_line_ids': bom_line_ids
        # }
        # bom_id = BOM.create(obj)
        # bom_id.onchange_product_id()
        # bom_id._check_bom_lines()
        # bom_id.onchange_product_uom_id()
        # bom_id.onchange_product_tmpl_id()
        # bom_id.check_kit_has_not_orderpoint()

        # self.bom_id = bom_id.id
        # if not self.component_line_ids or not self.hardware_line_ids or not self.special_material_line_ids:
        #     raise ValidationError("All fields (Component, Hardware, and Special Material) must have at least one record before creating BOM.") 
        # else:
        #     self.write({'is_bom_created': True})    
    
    def send_to_marketing(self):
        for rec in self:
            rec.state = 'marketing_review'
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    def start_draw(self):
        for rec in self:
            rec.state = 'processing'
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

    def end_draw(self):
        for rec in self:
            rec.state = 'to_review'
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',

            }

    # def end_draw(self):
    #     import pdb;pdb.set_trace()
    #     for rec in self:
    #         rec.state = 'to_review'
    #     design_process = self.design_process_id
    #     for dp in design_process:
    #         code = dp.stage_id.code
    #         print("Code for stage_id:", code)
    #         if code == 'design':
    #             code = 'sample'
                
        # return {
        #     'name' : _("Approve Manager With Comment"),
        #     'view_type' : 'form',
        #     'res_model' : 'design.process',
        #     'view_mode' : 'form',
        #     'type':'ir.actions.act_window',
        #     'target': 'current',
        #     }
        

    def approve(self):
        for rec in self:
            rec.state = 'confirm'
        return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
class VerifikasiDesign(models.Model):
    _inherit = 'verifikasi.design'

    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    attachment1 = fields.Binary("Attachments")
    attachment2 = fields.Binary("Attachments")
    attachment3 = fields.Binary("Attachments")
    attachment4 = fields.Binary("Attachments")
    attachment5 = fields.Binary("Attachments")
    attachment6 = fields.Binary("Attachments")
    attachment7 = fields.Binary("Attachments")

class SketWarna(models.Model):
    _inherit = 'sket.warna'

    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    attachment1 = fields.Binary("Attachments 1", track_visibility="onchange")
    attachment2 = fields.Binary("Attachments 2", tracking=3)
    attachment3 = fields.Binary("Attachments 3", tracking=3)
    attachment4 = fields.Binary("Attachments 4", tracking=3)
    attachment5 = fields.Binary("Attachments 5", tracking=3)
    attachment6 = fields.Binary("Attachments 6", tracking=3)
    attachment7 = fields.Binary("Attachments 7", tracking=3)
    
    # def tes_sket(self):
    #     import pdb; pdb.set_trace()
    #     attach = self.env['ir.attachment'].sudo().search([('res_model','=','sket.warna'),('res_id','=',self.id)])

    #     attach = self.env['ir.attachment'].sudo().search([('res_model','=',self._name),('res_id','=',self.id)])
        
        
    #     # attach = self.env['ir.attachment'].search([('type','=','binary'),('res_id','=', self.id),('res_model','=','sket_warna')])
    #     return
    
    
    # def write(self, values):
    #     _logger.info("======VAUES  SKET WARNA RND FLOW========")
    #     _logger.info(values)
        
    #     return super(SketWarna, self).write(values)

class ExplodeDiagram(models.Model):
    _inherit = 'explode.diagram'

    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    attachment1 = fields.Binary("Attachments")
    attachment2 = fields.Binary("Attachments")
    attachment3 = fields.Binary("Attachments")
    attachment4 = fields.Binary("Attachments")
    attachment5 = fields.Binary("Attachments")
    attachment6 = fields.Binary("Attachments")
    attachment7 = fields.Binary("Attachments")

class SketDetail(models.Model):
    _inherit = 'sket.detail'
    
    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    attachment1 = fields.Binary("Attachments")
    attachment2 = fields.Binary("Attachments")
    attachment3 = fields.Binary("Attachments")
    attachment4 = fields.Binary("Attachments")
    attachment5 = fields.Binary("Attachments")
    attachment6 = fields.Binary("Attachments")
    attachment7 = fields.Binary("Attachments")



class DesignDetailBomLine(models.Model):
    _name = 'design.detail.bom.line'
    _description = 'Design Detail Bom Line'
    # _inherit = 'stock.quant'

    
    standard_price = fields.Float(string="Cost",readonly=False,store=True)
    sub_cost = fields.Float('Subtotal Cost',digits='Product Unit of Measure' ,store=True, compute="_get_sub_cost")
    # selec = fields.Char(string="Category")
    @api.depends('standard_price', 'product_qty')
    def _get_sub_cost(self):
        for line in self:
            line.sub_cost = line.standard_price * line.product_qty

    # def _get_default_product_uom_id(self):
    #     return self.env['uom.uom'].search([], limit=1, order='id').id

    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    product_code = fields.Char('Code', store=True)
    # code = fields.Char('product.code', string='Code')
    location_id = fields.Many2one('stock.location', 'Destination Location', required=False, readonly=False )
    rasio = fields.Integer('Rasio')
    model = fields.Char('Model')
    component = fields.Char('Component')
    sale_ok = fields.Boolean('Can be Sold')
    purchase_ok = fields.Boolean('Can be Purchase')
    is_manufacture = fields.Boolean('Is Manufacture?')
    type = fields.Selection([
        ('consu', 'Consumable'),
        ('service', 'Service'),
        ('product', 'Storable Product')], string='Product Type', default='product',required=True,
        help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
             'A consumable product is a product for which stock is not managed.\n'
             'A service is a non-material product you provide.')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template')
    product_id = fields.Many2one('product.product', string='Product', required=False, readonly=False)
    categ_id = fields.Many2one(
        'product.category', 'Product Category',
        change_default=True, group_expand='_read_group_categ_id',
        default=lambda self: self.env['product.category'].search([], limit=1).id,
        help="Select category for the current product" )

  
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure',
        # default=_get_default_product_uom_id,
        store=True,readonly=False,required=True,
        help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control")
    
    # def create_revise_document(self):
    #     for rec in self:
    #         new_document = rec.design_detail_id.copy({'state': 'draft', 'origin_id': rec.design_detail_id.id})
    #         new_document.name = rec.design_detail_id.name + ' (Revised)'
    #         rec.design_detail_id.state = 'revised'
    #         for line in new_document.component_line_ids:
    #             if line.type != 'product':
    #                 raise ValidationError('Quants cannot be created for consumables or services.')
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'reload',
    #     }



    # product_uom_id = fields.Many2one(
    #     'uom.uom', 'Unit of Measure',
    #     store=True, 
    #     readonly=False, 
    #     help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control")
   
    # product_uom_id = fields.Many2one(
    #     'uom.uom', 'Unit of Measure',
    #     store=True,required=True,
    #     readonly=False,
    #     default=lambda self: self.env.ref('uom.product_uom_unit').id,
    #     help="Unit of Measure (Unit of Measure) is the unit of measurement for the inventory control"
    # )

    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True,store=True)
    size_panjang = fields.Float("P")
    size_lebar = fields.Float("L")
    size_tebal = fields.Float("T")
    total_meter_cubic = fields.Float("Cubic (M³)", digits=(12,5), compute="get_calc")
    total_meter_persegi = fields.Float("Persegi (M²)", digits=(12,5), compute="get_calc")
    description = fields.Char("Description")

    @api.depends('size_panjang', 'size_lebar','size_tebal','product_qty')
    def get_calc(self):
        for cal in self:
            meter3 = cal.size_panjang * cal.size_lebar * cal.size_tebal
            meter2 = (cal.size_panjang * cal.size_lebar) + (cal.size_panjang * cal.size_tebal) + (cal.size_lebar * cal.size_tebal)
    # size_cm
    #       cal.total_meter_cubic = ((meter3) / 1000000) * cal.product_qty if meter3 > 0 else 0.00
    #       cal.total_meter_persegi = ((meter2) / 10000) * cal.product_qty if meter2 > 0 else 0.00
    # size_mm
            cal.total_meter_cubic = ((meter3) / 1000000000) * cal.product_qty if meter3 > 0 else 0.00
            cal.total_meter_persegi = ((meter2) / 1000000) * cal.product_qty if meter2 > 0 else 0.0

    # def _default_categ_id(self):
    #     categ_id = self.env['product.category'].search([('name', '=', 'All')], limit=1)
    #     return categ_id
class DesignDetailHardware(models.Model):
    _name = 'design.detail.hardware'
    _description = 'Design Detail Hardware'

    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    
    product_id = fields.Many2one('product.product', string='Item',domain=[('categ_id.name', '=', 'Hardware')])
    description = fields.Text('Description')
    standard_price = fields.Float(string='Cost')

    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)

    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     if self.product_id and self.product_id.uom_id:
    #         self.product_uom = self.product_id.uom_id.id

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.standard_price = self.product_id.standard_price

class DesignDetailSpecialMaterial(models.Model):
    _name = 'design.detail.special.material'
    _description = 'Design Detail Special Materials'

    design_detail_id = fields.Many2one('design.detail', string='Design Detail')
    product_id = fields.Many2one('product.product', string='Item',domain=[('categ_id.name', 'in', ['Gudang Cat','Saleable','Aneka','Kanvas','Karton'])])
    description = fields.Text('Description')
    standard_price = fields.Float(string='Cost')

    product_qty = fields.Float(
        'Quantity', default=1.0,
        digits='Product Unit of Measure', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    
    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     if self.product_id and self.product_id.uom_id:
    #         self.product_uom = self.product_id.uom_id.id

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.standard_price = self.product_id.standard_price