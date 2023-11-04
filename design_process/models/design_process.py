# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError




class design_process(models.Model):
    _name = 'design.process'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Design Process'

    partner_team = fields.Many2one('res.partner', string='RnD Teams')

    #signature data
    name_rnd_manager = fields.Char(string='R&D Manager')
    name_marketing_department = fields.Char(string='Marketing Department')
    name_rnd_department = fields.Char('R&D Department')
    name_marketing_manager = fields.Char('Marketing Manager')
    ttd_rnd_manager = fields.Binary('Signature R&D Manager')
    ttd_marketing_department = fields.Binary('Signature Marketing Department')
    ttd_rnd_department = fields.Binary('Signature R&D Department')
    ttd_marketing_manager = fields.Binary('Signature Marketing Manager')
    
    name = fields.Char('Name', copy=False, default='New RND', required=True, readonly=True)
    partner_id = fields.Many2one("res.partner","Customer")
    deadline = fields.Date('Deadline')
    other_note = fields.Text('Note')
    schedule_date = fields.Date('Schedule Date')
    schedule_design = fields.Date('Schedule Design')
    schedule_image = fields.Date('Schedule Image')
    department_id = fields.Many2one('hr.department','Department')
    user_id = fields.Many2one("res.users","Person In Charge (Marketing)")
    spec_design_ids = fields.One2many('spec.design','design_process_id','Spec Design')
    material_ids = fields.One2many('spec.design.line','design_process_id','Material', readonly=True)
    special_ids = fields.One2many('spec.intruction','design_process_id','Special Instruction', readonly=True)
    hardware_ids = fields.One2many('hardware.design.line','design_process_id','Material')
    is_set = fields.Boolean("Is Set", default=False)
    item = fields.Many2one("product.product",'Item. Spec Design')
    request_no = fields.Char("No. Spec Design",readonly=True, copy=False)
    detail_material_ids = fields.Many2many('design.material','masterial_ref_name_matrial','material_rgt_name_id','material_ref_name_id','Material')
    detail_finish_ids = fields.Many2many('design.finish','design_ref_name_finish','design_ref_id','name_fish_finish_id','Finish')
    crm_id = fields.Many2one('crm.lead',"Spec. Design")
    stage_id = fields.Many2one('design.process.stage','Stage', required=True,
        default=lambda self: self.stage_id.search([('name','=','Draft')], limit=1),
        group_expand='_group_expand_stage_ids',copy=False)
    

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
    work_order_count = fields.Integer("Work Order Count", compute="count_pembahanan")
    sale_order_count = fields.Integer("Sale Order Count", compute="count_pembahanan")
    pembahanan_count = fields.Integer("Pembahanan Count", compute="count_pembahanan")
    costing_count = fields.Integer("Costing Count", compute="count_pembahanan")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('done', 'Done')],
        string='Kanban State',default='draft')


    type_rnd = fields.Selection([
        ('is_sample', 'Is Sample Request'),
        ('is_design', 'Is Spec Design')],
        string='Type RnD', copy=True)

    approval_history_ids = fields.One2many("approval.history","design_id","Approval History")
    is_asigned = fields.Boolean("is_asigned", default=False)
    


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
        res = super(design_process, self).create(vals)
        return res


    @api.onchange("user_team_id")
    def get_teams_rnd(self):
        user = self.user_team_id
        if user:
            self.user_rnd_id = user.partner_id.id
            self.department_rnd_id = user.department_id.id
            # self.department_rnd_id = user.department_rnd_id.id
            self.rnd_team_id = user.team_rnd_id.id


    @api.onchange('schedule_design',"deadline")
    def change_schedule(self):
        if self.schedule_design and self.deadline:
            if self.schedule_design > self.deadline:
                raise UserError(_("Schedule Design Tidak Bisa Melebihi Deadline"))


    def count_pembahanan(self):
        res = self.env['mrp.bom'].search_count([('rnd_id', '=', self.id)])
        sale = self.env['sale.order'].search_count([('opportunity_id','=', self.crm_id.id)])
        mrp = self.env['mrp.production'].search_count([('rnd_id','=', self.id)])
        # mrp = self.env['mrp.production'].search_count([('request_no','=', self.request_no)])
        cost = self.env['summary.costing'].search_count([('request_no','=', self.request_no)])
        self.pembahanan_count = res
        self.sale_order_count = sale
        self.work_order_count = mrp
        self.costing_count = cost

    @api.onchange("is_set")
    def change_item(self):
        if not self.is_set:
            self.item= False

    
    def action_confirm(self):
        return {
                'name' : _("Confirm With Comment"),
                'view_type' : 'form',
                'res_model' : 'approval.history.rnd.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
            }

    # def action_sket(self):
    #     return {
    #             'name' : _("Sket Colour With Comment"),
    #             'view_type' : 'form',
    #             'res_model' : 'approval.history.rnd.wizard',
    #             'view_mode' : 'form',
    #             'type':'ir.actions.act_window',
    #             'target': 'new',
    #         }

    def action_set_to_draft(self):
        stage_draft = self.stage_id.search([('code','=','draft')])
        user = self.env.user
        mstr = [(0,0,{
            'stage_id' : "Set To Draft",
            'user_id' : user.id,
            })]
        self.approval_history_ids = mstr
        self.stage_id = stage_draft.id
        for line in self.spec_design_ids:
            line.process_state = 'draft'



    
    def action_perincian_design(self):
        return {
                'name' : _("Confirm With Comment"),
                'view_type' : 'form',
                'res_model' : 'approval.history.rnd.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
            }

    def action_revisi_rnd(self):
        view = self.env.ref('jidoka_rnd_flow.wizard_design_detail_revised_view_form')
        # domain = [('crm_id','=',self.id),('state','in',('marketing_review','in_review'))]
        return {
            'name': _('Design Detail Revised'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'wizard.design.detail.revised',
            'views': [(view.id, 'form')],
            # 'domain' : domain,
            'view_id': view.id,
            'target': 'new',
            'context':{
                'default_crm_id':self.crm_id.id,
                'default_parent_domain':'marketing_review', 
                # 'default_parent_domain':'to_review',
                'default_is_need_revised':True,
                # 'default_type_button':'revisi',
                # 'default_detail_line_ids': self.ids
            }
        }

    def action_perincian_sample(self):
        return {
                'name' : _("Confirm With Comment"),
                'view_type' : 'form',
                'res_model' : 'approval.history.rnd.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
            }


    def action_approve_manager(self):
        return {
                'name' : _("Confirm With Comment"),
                'view_type' : 'form',
                'res_model' : 'approval.history.rnd.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
            }

    def action_to_sale(self):
        return {
                'name' : _("Assigned to Sale With Comment"),
                'view_type' : 'form',
                'res_model' : 'approval.history.rnd.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
            }

    def action_validate_process(self):
        stage = self.stage_id.search([('code','=','process')])
        self.stage_id = stage.id
        
    def action_done(self):
         return {
                'name' : _("Done Process With Comment"),
                'view_type' : 'form',
                'res_model' : 'approval.history.rnd.wizard',
                'view_mode' : 'form',
                'type':'ir.actions.act_window',
                'target': 'new',
            }


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

    # def get_work_order(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Manufacturing Orders',
    #         'view_mode': 'tree,form',
    #         'res_model': 'mrp.production',
    #         'domain': [('rnd_id', '=', self.id)],
    #         'context': "{'create': False}"
    #     }

    def get_work_order(self):
        # self.ensure_one()
        work_order_domain = [('request_no', '=', self.request_no)]
        work_order_data = {
            'rnd_id': self.id,
        }
        
        self.env['mrp.production'].search(work_order_domain).write(work_order_data)
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Manufacturing Orders',
            'view_mode': 'tree,form',
            'res_model': 'mrp.production',
            'domain': work_order_domain,
            'context': "{'create': False}"
        }
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Manufacturing Orders',
        #     'view_mode': 'tree,form',
        #     'res_model': 'mrp.production',
        #     'domain': [('request_no', '=', self.request_no)],
        #     'context': "{'create': False}"
        # }


    def get_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotation',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('opportunity_id', '=', self.crm_id.id)],
            'context': "{'create': False}"
        }

    def get_action_bom(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'BoM',
            'view_mode': 'tree,form',
            'res_model': 'mrp.bom',
            'domain': [('rnd_id', '=', self.id)],
        }

    def action_outstanding_bom(self):
        bom = self.env['mrp.bom'].search([('product_tmpl_id','=', self.item.product_tmpl_id.id)])
        bom_line_ids = []
        if not bom and self.is_set:
            for line in self.spec_design_ids:
                bom_line_ids.append((0,0,{
                    'product_id': line.item_id.id,
                    'product_qty': line.quantity
                }))
            obj = {
                'product_tmpl_id': self.item.product_tmpl_id.id,
                'product_qty': 1,
                'product_uom_id': self.item.uom_id.id,
                'code': self.name,
                'rnd_id': self.id,
                'crm_id': self.crm_id.id,
                'bom_line_ids': bom_line_ids
            }
            bom.create(obj)
            bom.onchange_product_id()
            bom._check_bom_lines()
            bom.onchange_product_uom_id()
            bom.onchange_product_tmpl_id()
            bom.check_kit_has_not_orderpoint()

        if not bom and not self.is_set:
            for line in self.spec_design_ids:
                obj = {
                    'product_tmpl_id':line.item_id.product_tmpl_id.id,
                    'product_qty': line.quantity,
                    'product_uom_id': line.item_id.uom_id.id,
                    'type_bom': 'is_design',
                    'code': self.name,
                    'rnd_id': self.id,
                    'crm_id': self.crm_id.id,

                }
                bom.create(obj)
                bom.onchange_product_id()
                bom._check_bom_lines()
                bom.onchange_product_uom_id()
                bom.onchange_product_tmpl_id()
                bom.check_kit_has_not_orderpoint()

        if bom:
            bom.write({'rnd_id': self.id, 'crm_id': self.crm_id.id})




    def action_create_sample(self):
        for line in self.spec_design_ids:
            if self.item:
                product = self.item
            else:
                product = line.item_id
            vals = {
                'product_id': product.id,
                'product_qty': line.quantity,
                'product_uom_id': product.uom_id.id,
                'rnd_id': self.id,
                'origin': self.name,
                'request_no': self.request_no,
                'is_sample_request': True
            }
            mrp = self.env['mrp.production'].create(vals)
            mrp.onchange_company_id()
            mrp.onchange_product_id()
            mrp._onchange_product_qty()
            mrp._onchange_bom_id()
            mrp._onchange_date_planned_start()
            mrp._onchange_move_raw()
            mrp._onchange_move_finished_product()
            mrp._onchange_move_finished()
            mrp._onchange_location()
            mrp._onchange_location_dest()
            mrp.onchange_picking_type()
            mrp._onchange_producing()
            mrp._onchange_lot_producing()
            mrp._onchange_workorder_ids()
            user = self.env.user
            mstr = [(0,0,{
                    'stage_id' : "Create Sample",
                    'comment' : "%s Has been Created" %(mrp.name),
                    'user_id' : user.id,
                })]
            self.approval_history_ids = mstr
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Process Sample Has Been Created',
                    'type': 'rainbow_man',
                }
            }


    def action_costing(self):
        for res in self:
            for line in res.spec_design_ids:
                actual_cost = []
                pws = line
                gnr = line
                for cost in pws.material_ids:
                    actual_cost.append((0,0,{
                        'product_id' : cost.product_id.id,
                        }))
                hardware = []
                for ks in gnr.hardware_ids:
                    hardware.append((0,0,{
                        'product_id' : ks.product_id.id,
                        }))
                design = {
                    # 'item_no' : res.item,
                    'item_id': line.item_id.id,
                    'request_no' : res.request_no,
                    'wood_costing_line_ids' : actual_cost,
                    'hadware_costing_line_ids' : hardware
                }
                cost = self.env['summary.costing']
                cost.create(design)
                




class jidoka_spec_inherit(models.Model):
    _inherit = 'spec.design'
    _description = 'Details Design'

    design_process_id = fields.Many2one("design.process","Design Process")
    request_no = fields.Char("Request No", related="design_process_id.request_no")





class jidoka_spec_line(models.Model):
    _inherit = 'spec.design.line'
    _description = 'Details Design Line'

    design_process_id = fields.Many2one("design.process","Design Process")


class jidoka_spec_intruction(models.Model):
    _inherit = 'spec.intruction'
    _description = 'Spec Instruction'

    design_process_id = fields.Many2one("design.process","Design Process")


class jidoka_hardware_intruction(models.Model):
    _inherit = 'hardware.design.line'
    _description = 'Spec Intruction'

    design_process_id = fields.Many2one("design.process","Design Process")