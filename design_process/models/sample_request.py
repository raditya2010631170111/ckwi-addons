from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError

class SampleRequest(models.Model):
    _name = 'sample.request'


    partner_team = fields.Many2one('res.partner', string='RnD Teams')
    purpose = fields.Char(string='Purpose', required=True, tracking=True, 
    default="Sample Request from RnD")
    pricelist_id = fields.Many2one('product.pricelist', "Currency")
    is_r = fields.Boolean(
    default=False
    )
    #signature data
    name_rnd_manager = fields.Char(string='R&D Manager')
    name_marketing_department = fields.Char(string='Marketing Department')
    name_rnd_department = fields.Char('R&D Department')
    name_marketing_manager = fields.Char('Marketing Manager')
    ttd_rnd_manager = fields.Binary('Signature R&D Manager')
    ttd_marketing_department = fields.Binary('Signature Marketing Department')
    ttd_rnd_department = fields.Binary('Signature R&D Department')
    ttd_marketing_manager = fields.Binary('Signature Marketing Manager')
    # crm_sample_request_id = fields.Many2one('crm.sample.request', string='Sample Request')
    no_sample = fields.Char(string='Sample Request')  
    name = fields.Char('Name', copy=False, default='New RND', required=True, readonly=True)
    partner_id = fields.Many2one("res.partner","Customer")
    deadline = fields.Date('Date Deadline', 
    required=True)
    other_note = fields.Text('Note')
    schedule_date = fields.Date('Date Issued')
    schedule_design = fields.Date('Schedule Design')
    schedule_image = fields.Date('Schedule Image')
    department_id = fields.Many2one('hr.department','Department')
    user_id = fields.Many2one("res.users","Salesperson")
    sample_ids = fields.One2many('line.sample.request','sample_id','sample request')
    material_ids = fields.One2many('spec.design.line','design_process_id','Material', readonly=True)
    special_ids = fields.One2many('spec.intruction','design_process_id','Special Instruction', readonly=True)
    hardware_ids = fields.One2many('hardware.design.line','design_process_id','Material')
    is_set = fields.Boolean("Is Set", default=False)
    item = fields.Many2one("product.product",'Item. Spec Design')
    request_no = fields.Char("No. Spec Design", copy=False)
    detail_material_ids = fields.Many2many('design.material', string='Detail Materials')
    detail_finish_ids = fields.Many2many('design.finish' , string='Detail Finishes')

    crm_id = fields.Many2one('crm.lead',"Spec. Design")
    stage_id = fields.Many2one('design.process.stage','Stage', required=True,
        default=lambda self: self.stage_id.search([('name','=','Draft')], limit=1),
        group_expand='_group_expand_stage_ids',copy=False)
    stated = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('rev', 'Revised')
    ], string='Status', readonly=True, copy=False, default='draft', track_visibility='onchange')

    state_type = fields.Char("State Type", related="stage_id.code")
    user_rnd_id = fields.Many2one("res.partner", string='Partner RnD')
    user_team_id = fields.Many2one("res.users", string='RnD Person')
    rnd_team_id = fields.Many2one("team.rnd","RnD Teams")
    department_rnd_id = fields.Many2one("hr.department","Department")
    kanban_state = fields.Selection([
        ('done', 'Green'),
        ('check', 'Yellow'),
        ('blocked', 'Red')],
        string='Kanban State',default='done') 
 
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('done', 'Done')],
        string='Kanban State',default='draft')


    type_rnd = fields.Selection([
        ('is_sample', 'Is Sample Request'),
        ('is_design', 'Is Spec Design')],
        string='Type RnD', copy=True, 
        default='is_sample', readonly=True
        )

    approval_history_ids = fields.One2many("approval.history","design_id","Approval History")
    is_asigned = fields.Boolean("is_asigned", default=False)
    internal_notes = fields.Text(string="Internal Notes")


    @api.model
    def _group_expand_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)


    @api.model
    def create(self, vals):
        if vals.get('name', 'New RND') == 'New RND':
           vals['name'] = self.env['ir.sequence'].next_by_code('rnd.request') or 'New RND'
        res = super(SampleRequest, self).create(vals)
        return res


    @api.onchange("user_team_id")
    def get_teams_rnd(self):
        user = self.user_team_id
        if user:
            self.user_rnd_id = user.partner_id.id
            self.department_rnd_id = user.department_id.id
            # self.department_rnd_id = user.department_rnd_id.id
            self.rnd_team_id = user.team_rnd_id.id
    def draft(self):
        for rec in self:
            rec.write({'stated': 'draft'})
    
    def approve(self):
        for rec in self:
            rec.write({'stated': 'approve'})

    def submit(self):
        for rec in self:
            rec.write({'stated': 'submit'})

    def reject(self):
        for rec in self:
            rec.write({'stated': 'reject'})

    @api.onchange('schedule_design',"deadline")
    def change_schedule(self):
        if self.schedule_design and self.deadline:
            if self.schedule_design > self.deadline:
                raise UserError(_("Schedule Design Tidak Bisa Melebihi Deadline"))


    def check_rev(self):
        self.write({
            'stated': 'rev'
        })
        
        old_request_no = self.name or 'New'

        if old_request_no.endswith('.Rev'):
            if old_request_no.split('.Rev-')[-1].isdigit():
                rev_number = int(old_request_no.split('.Rev-')[-1])
                new_rev_number = rev_number + 1
                new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"
            else:
                new_request_no = f"{old_request_no}.Rev-01"
        else:
            new_request_no = f"{old_request_no}.Rev-01"

        rev_numbers = [
            int(x.split('.Rev-')[-1]) 
            for x in self.search([('name', 'like', f'{old_request_no.rsplit(".Rev-", 1)[0]}%.Rev-')]).mapped('name')
        ]
        
        if rev_numbers:
            new_rev_number = max(rev_numbers) + 1
            new_request_no = f"{old_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"

        while self.env['sample.request'].search_count([('name', '=', new_request_no)]) > 0:
            rev_number = int(new_request_no.split('.Rev-')[-1])
            new_rev_number = rev_number + 1
            new_request_no = f"{new_request_no.rsplit('.Rev-', 1)[0]}.Rev-{new_rev_number:02d}"

        vals = {
            'name': new_request_no,
            'request_no': self.request_no,
            'crm_id': self.crm_id.id,
            'no_sample': self.no_sample,
            'partner_id': self.partner_id.id,
            'stated' : 'draft',
            'partner_team': self.partner_team.id,
            'purpose': self.purpose,
            'schedule_date': self.schedule_date,
            'deadline': self.deadline,
            'detail_material_ids': [(6, 0, self.detail_material_ids.ids)],
            'detail_finish_ids': [(6, 0, self.detail_finish_ids.ids)],
            'user_id': self.user_id.id,
            # 'company_id': self.company_id.id,
            'department_id': self.department_id.id,
            'user_rnd_id': self.user_rnd_id.id,
            'user_team_id': self.user_team_id.id,
            'rnd_team_id': self.rnd_team_id.id,
            'department_rnd_id': self.department_rnd_id.id,
            'type_rnd': self.type_rnd,
            'pricelist_id': self.pricelist_id.id,
       }

        new_record = self.env['sample.request'].create(vals)

        line_spec = []
        for line_ids in self.sample_ids:
            line_spec.append((0, 0, {
                'item_id': line_ids.item_id.id,
                'quantity': line_ids.quantity,
                'uom_id': line_ids.uom_id.id,
                'remark': line_ids.remark,
                'description': line_ids.description,
                'attachment': line_ids.attachment,
                'attachment2': line_ids.attachment2,
                'attachment3': line_ids.attachment3,
            }))
        self.is_r = True
        new_record.write({'sample_ids': line_spec})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sample.request',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': new_record.id,
            'target': 'current',
        }

    @api.onchange("is_set")
    def change_item(self):
        if not self.is_set:
            self.item= False

class LineSampleRequest(models.Model):
    _name  = 'line.sample.request'
    _description = 'Details Design'
    
    remark = fields.Text('Remark', strip_style=True)
    sample_id = fields.Many2one("sample.request","Design Process")
    crm_id = fields.Many2one("crm.lead","CRM")
    item_id = fields.Many2one('product.product','Product Design', required=True)
    item = fields.Many2one("product.product",'Item. Spec Design',related='crm_id.item')
    description = fields.Text('Description')
    attachment = fields.Image('Image1', max_width=512, max_height=512, store=True)
    attachment2 = fields.Image('Image2', max_width=512, max_height=512, store=True)
    attachment3 = fields.Image('Image3', max_width=512, max_height=512, store=True)
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