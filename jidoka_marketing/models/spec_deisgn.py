
from odoo import models, fields, api, _




class jidoka_spec(models.Model):
    _name = 'spec.design'
    _description = 'Details Design'


    crm_id = fields.Many2one("crm.lead","CRM")
    item_id = fields.Many2one('product.product','Product Design', required=True)
    item = fields.Many2one("product.product",'Item. Spec Design',related='crm_id.item')
    description = fields.Text('Description')
    attachment = fields.Image('Design Image', max_width=512, max_height=512, store=True)
    # attachment2 = fields.Image('Image2', max_width=512, max_height=512, store=True)
    # attachment3 = fields.Image('Image3', max_width=512, max_height=512, store=True)
    ref_attachment = fields.Image('Reference Image', max_width=512, max_height=512, store=True)
    prod_referency_id = fields.Many2one('product.product','Product Reference')
    quantity = fields.Float('Quantity', default=1)
    unit_price = fields.Float('Unit Price', default=1)
    sub_total = fields.Float('Total', compute='get_sub_total')
    uom_id = fields.Many2one("uom.uom","Unit Of Measure")
    note = fields.Text('Note', strip_style=True)
    other_note = fields.Text('Note')
    production_location_id = fields.Many2one('stock.location', "Production Location", store=True)
    location_dest_id = fields.Many2one(
        'stock.location', 'Finished Products Location',
        help="Location where the system will stock the finished products.")
    bill_of_material_id = fields.Many2one('mrp.bom','Ref MRP Bom')
    material_ids = fields.One2many('spec.design.line','spec_id','Material')
    hardware_ids = fields.One2many('hardware.design.line','spec_id','Material')
    special_ids = fields.One2many('spec.intruction','spec_id','Special Instruction')
    process_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting'),
        ('process', 'Process'),
        ('done', 'Done')],
        string='State',default='draft')

    design_image = fields.One2many("design.image","spec_id", string="Image", 
        max_width=512, max_height=512, store=True)

    verifikasi_design = fields.One2many("verifikasi.design","spec_id", string="Verifikasi Design", 
        max_width=512, max_height=512, store=True)

    sket_warna = fields.One2many("sket.warna","spec_id", string="Sket Warna",
        max_width=512, max_height=512, store=True)

    explode_diagram = fields.One2many("explode.diagram","spec_id", string="Explode Diagram", 
        max_width=512, max_height=512, store=True)

    sket_detail = fields.One2many("sket.detail","spec_id", string="Sket Detail", 
        max_width=512, max_height=512, store=True)

    verifikasi_sample = fields.One2many("verifikasi.sample","spec_id", string="Sket Detail", 
        max_width=512, max_height=512, store=True)


    @api.depends('quantity','unit_price')
    def get_sub_total(self):
        for x in self:
            x.sub_total = x.quantity * x.unit_price

    @api.onchange("item_id")
    def get_uom_id(self):
        for c in self:
            uom = c.item_id.uom_id
            c.uom_id = uom


    def clean_data(self):
        self.material_ids.unlink()
        self.bill_of_material_id = False


    @api.onchange('bill_of_material_id')
    def get_lines(self):
        for spec in self:
            wjk = []    
            material = spec.bill_of_material_id
            if material:
                line = material.bom_line_ids
                for bill in line:
                    wjk = {
                        'product_id' : bill.product_id.id,
                        'quantity' : bill.product_qty,
                        'uom_id' : bill.product_uom_id.id,
                    }
                    spec.material_ids = [(0,0, wjk)]




class jidoka_spec_design_line(models.Model):
    _name = 'spec.design.line'
    _order = "category_id,sequence,id"
    _description = 'Details Design'

    sequence = fields.Integer("Sequence")
    spec_id = fields.Many2one("spec.design","Spec. Design")
    crm_id = fields.Many2one("crm.lead","CRM",related="spec_id.crm_id")
    product_id = fields.Many2one('product.product', 'Componen')
    category_id = fields.Many2one("product.category","Category", related="product_id.categ_id")
    quantity = fields.Float("Quantity", default=1)
    name = fields.Char("Nama Bagian")
    model = fields.Char("Model")
    unit_price = fields.Float("Unit Price")
    sub_total = fields.Float("Total",compute="get_total")
    note = fields.Char("Note")
    uom_id = fields.Many2one("uom.uom","Unit Of Measure")

    @api.onchange("product_id")
    def get_default_prod(self):
        for line in self:
            prod = line.uom_id.id
            line.uom_id = prod

    @api.depends('quantity','unit_price')
    def get_total(self):
        for c in self:
            c.sub_total = c.quantity * c.unit_price


class jidoka_hadware_design_line(models.Model):
    _name = 'hardware.design.line'
    _description = 'Hardware Design'


    spec_id = fields.Many2one("spec.design","Spec. Design")
    crm_id = fields.Many2one("crm.lead","CRM",related="spec_id.crm_id")
    product_id = fields.Many2one('product.product', 'Componen')
    quantity = fields.Float("Quantity", default=1)
    name = fields.Char("Nama Bagian")
    model = fields.Char("Model")
    unit_price = fields.Float("Unit Price")
    sub_total = fields.Float("Total",compute="get_total")
    note = fields.Char("Note")
    uom_id = fields.Many2one("uom.uom","Unit Of Measure")

    @api.onchange("product_id")
    def get_default_prod(self):
        for line in self:
            prod = line.product_id.uom_id.id
            line.uom_id = prod

    @api.depends('quantity','unit_price')
    def get_total(self):
        for c in self:
            c.sub_total = c.quantity * c.unit_price


class jidoka_spec_intr(models.Model):
    _name = 'spec.intruction'
    _description = 'Spec Intruction'




    spec_id = fields.Many2one("spec.design","Spec. Design")
    crm_id = fields.Many2one("crm.lead","CRM",related="spec_id.crm_id")
    note = fields.Char("Instruction")

