# -*- coding: utf-8 -*-

from datetime import datetime, time
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import calendar as cal

class Users(models.Model):
    _inherit = "res.users"


class HrEquipmentStage(models.Model):
    _inherit = 'maintenance.stage'

    status = fields.Char(string='Status', translate=False)
    custom_user_ids = fields.Many2many('res.users')

    @api.onchange('name')
    def onchange_state(self):
        self.status = self.name

class HrEquipmentRequest(models.Model):
    _inherit = 'maintenance.request'
    _order = "priority desc, id desc"

    maintenance_plan_id = fields.Many2one(string="Maintenance Plan", comodel_name="maintenance.plan", ondelete="restrict")
    maintenance_timetable_id = fields.Many2one(string="Maintenance Timetable", comodel_name="maintenance.timetable", ondelete="restrict")
    maintenance_daily_id = fields.Many2one(string="Maintenance Daily", comodel_name="maintenance.daily", ondelete="restrict")

    wo_number = fields.Char('WO Number', copy=False, default=lambda self: _('New'), required=True)
    note = fields.Html("Note")
    analisa = fields.Html('Analisa', translate=True)
    penyelesaian = fields.Html('Penyelesaian', translate=True)
    state = fields.Selection([('new', 'New Request'),
                              ('first_approval', 'First Approval'),
                              ('second_approval', 'Second Approval'),
                              ('in_progress', 'In Progress'),
                              ('repair', 'Repaired'),
                              ('done', 'Done'),
                              ('cancel', 'Cancel')], default='new', string='Status', translate=False)
    equipment_location = fields.Char(related='equipment_id.location', string='Equipment Location')
    location_id = fields.Many2one('stock.location', 'Destination Location')
    nama_mesin = fields.Char(related='equipment_id.name', string='Nama Mesin')
    no_mesin = fields.Char(related='equipment_id.serial_no', string='No Mesin')
    desc = fields.Char('Description')
    consumed_material_ids = fields.One2many('maintenance.consumed.material','consumed_maintenance_request_id', string='Consumed Materials')
    checklist_ids = fields.One2many('maintenance.checklist', 'maintenance_id', 'Check')
    checklist_line_ids = fields.One2many('maintenance.checklist.line', 'maintenance_id', "CheckList Lines")
    product_id = fields.Many2one('product.product', 'Product')
    qty = fields.Float('Quantity')
    uom_id = fields.Many2one('uom.uom', 'UOM')
    equipment_ids = fields.One2many('equipment.part.line', 'maintenance_id', string='Eqipment')
    project_task_id = fields.Many2one('project.task', "Job Order")
    is_project_task = fields.Boolean('Is Job Order ?', default=False, copy=False)
    is_material_requisition = fields.Boolean('Is Material Requisition?', default=False, copy=False)
    is_consume_transfer = fields.Boolean('Is Consume?', default=False, copy=False)
    partner_req_vendor_id = fields.Many2one('res.partner', 'Equipment Purchase Requisition Vendor')
    priority = fields.Selection(
        [('0', 'Very Low'), ('1', 'Low'), ('2', 'Normal'), ('3', 'High')],
        default='0', index=True, string="Priority")
    # stage_id = fields.Many2one("maintenance.stage", readonly=True)
    date_planned_start = fields.Datetime('Scheduled Date Start', index=True, copy=False, required=True,
        default=fields.Datetime.now,track_visibility='onchange', compute='_compute_schedule_planned_date')
    date_planned_finished = fields.Datetime('Scheduled Date Finished', copy=False, required=True,
        default=fields.Datetime.now,track_visibility='onchange')
    planned_duration = fields.Float('Planned Duration', store=True, copy=False)
    date_actual = fields.Date('Actual Date', copy=False, store=True, compute='_compute_actual_date')
    date_started = fields.Datetime('Effective Start Date',copy=False, store=True, track_visibility='onchange')
    date_finished = fields.Datetime('Effective End Date',copy=False, track_visibility='onchange',)
    actual_duration = fields.Float('Actual Duration', store=True, copy=False, track_visibility='onchange')
    
    def action_draft(self):
        if self:
            return self.write({'state': 'new'})

    def action_confirmed(self):
        self.write({'state': 'first_approval'})

    def action_approve(self):
        self.write({'state': 'second_approval'})

    def button_start_working(self):
        self.ensure_one()
        return self.write({'state': 'in_progress', 'kanban_state': 'done','date_started': datetime.now()})

    def button_finish(self):
        date_finished = datetime.now()
        date_started = self.date_started
        if date_started and date_finished and self.state in ('in_progress'):
            finished= datetime.strftime(fields.Datetime.context_timestamp(self, date_finished), "%Y-%m-%d %H:%M:%S")
            started= datetime.strftime(fields.Datetime.context_timestamp(self, date_started), "%Y-%m-%d %H:%M:%S")
            date_finish = datetime.strptime(str(finished), "%Y-%m-%d %H:%M:%S")
            date_start = datetime.strptime(str(started), "%Y-%m-%d %H:%M:%S")
            actual_hours = date_finish - date_start
            self.actual_duration = (actual_hours.seconds / 3600.00) + (actual_hours.days * 24.00)
            return self.write({'state': 'done', 'kanban_state': 'normal','actual_duration': self.actual_duration,'date_finished': datetime.now()})

    def cancel_wo(self):
        if self:
            return self.write({'state':'cancel'})

    @api.depends('schedule_date')
    def _compute_schedule_planned_date(self):
        for pd in self:
            pd.date_planned_start = pd.schedule_date

    @api.depends('date_started')
    def _compute_actual_date(self):
        for ac in self:
            ac.date_actual = ac.date_started

    @api.onchange('date_planned_finished')
    def onchange_planned_date(self):
        if self.date_planned_start and self.date_planned_finished:
            date_planned_start = datetime.strptime(str(self.date_planned_start), "%Y-%m-%d %H:%M:%S")
            date_planned_finished = datetime.strptime(str(self.date_planned_finished), "%Y-%m-%d %H:%M:%S")
            diff_hours = date_planned_finished - date_planned_start
            self.planned_duration = (diff_hours.seconds / 3600.00) + (diff_hours.days * 24.00)
        else:
            self.planned_duration = 0.00
    
    # ============================= CONSUME MAINTENANCE ================================================

    def display_consume_transfer(self):
        res = self.env.ref('fik_equipment_maintenance.action_comsume_transfer')
        res = res.read()[0]
        res['domain'] = str([('is_consume', '=', True)])
        return res
    # SET OPERATION TYPE
    def _default_operation_type(self):
        company_user = self.env.user.company_id
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)
             
        type_obj = self.env['stock.picking.type']
        types = type_obj.search([('consume_maintenance', '=', True), ('warehouse_id', '=', warehouse.id)], limit=1)
        if types:
            types =  types
        else:
            raise UserError(_('You must define a Operation Consume Maintenance for the company: %s.') % (company_user.name,))
        return types
    # CREATE PICKING
    def create_picking(self):
        if self.consumed_material_ids :
            picking_type = self._default_operation_type()
            pick = {
                        'picking_type_id'   : picking_type.id,
                        'location_dest_id'  : picking_type.default_location_dest_id.id,
                        'location_id'       : picking_type.default_location_src_id.id,
                        'origin'            : self.name,
                        'is_consume'        : True,
                    }

            picking = self.env['stock.picking'].create(pick)
            move = self.env['stock.move']
            for component in self.consumed_material_ids:
                line_com = {
                                'name'              : _('Component:') + component.product_id.display_name or '',
                                'product_id'        : component.product_id.id,
                                'product_uom_qty'   : component.product_uom_qty,
                                'product_uom'       : component.product_uom.id,
                                'location_id'       : picking_type.default_location_src_id.id,
                                'location_dest_id'  : picking_type.default_location_dest_id.id,
                                'picking_id'        : picking.id,
                                'state'             : 'draft',
                                'picking_type_id'   : picking.picking_type_id.id,
                            }
             
                move.create(line_com)
            picking.action_confirm()
            picking.action_assign()
        self.write({'is_consume_transfer': True})

    # =============END PICKING ========================================


    def check_validation(self):
        for rec in self:
            if not rec.schedule_date:
                raise UserError(_('Please Select Scheduled Date.'))
            if not rec.equipment_ids:
                raise UserError(_('Please Input Product in Part Material Machine.'))
            if not rec.location_id:
                raise UserError(_('Please Select Destination Location.'))
            if not rec.partner_req_vendor_id:
                raise UserError(_('Please Select Equipment Purchase Requisition Vendor.'))

    
    def display_job_order(self):

        res = self.env.ref('fik_equipment_maintenance.job_action')

        res = res.read()[0]
        res['domain'] = str([('maintenance_id', '=', self.id)])
        res['context'] = {
            'default_maintenance_id': self.id,
        }
        return res

    def create_purchase_requisition(self):
        for rec in self:
            self.check_validation()
            req_type = self.env['purchase.requisition.type'].search([('name', '=', 'Maintenance')])
            if not req_type:
                req_type = self.env['purchase.requisition.type'].create({
                    'name': 'Maintenance',
                    'quantity_copy': 'none'
                })
            for line in rec.equipment_ids:
                line_vals = (0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.qty,
                    'price_unit': line.product_id.standard_price,
                    'schedule_date': rec.schedule_date,
                })
            purchase_requisition_vals = {
                'user_id': rec.user_id.id,
                'type_id': req_type.id,
                'ordering_date': fields.Datetime.now(),
                'description': rec.description,
                'maintenance_id': rec.id,
                'schedule_date': rec.schedule_date,
                'vendor_id': rec.partner_req_vendor_id.id,
                'line_ids': [(0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.qty,
                    'price_unit': line.product_id.standard_price,
                    'schedule_date': rec.schedule_date,
                }) for line in rec.equipment_ids],
            }

            material_requisition = self.env['purchase.requisition'].create(
                purchase_requisition_vals)
            rec.is_material_requisition = True
        self.display_purchase_requisition()

    def display_purchase_requisition(self):
        res = self.env.ref('fik_equipment_maintenance.action_purchase_requisition')
        res = res.read()[0]
        res['domain'] = str([('maintenance_id', '=', self.id)])
        return res

    def write(self, vals):
        res = super(HrEquipmentRequest, self).write(vals)
        for request_id in self:
            if vals.get('equipment_id', False):

                equipment_data = self.env['maintenance.equipment'].browse(vals['equipment_id'])

                for check_id in equipment_data.check_ids:
                    checklist_vals = {
                        'name': check_id.name,
                        'desc': check_id.desc,
                        'maintenance_id': request_id.id,
                    }
                    self.env['maintenance.checklist.line'].create(checklist_vals)
                for line_id in equipment_data.line_ids:
                    equipment_part_line_vals = {
                        'product_id': line_id.product_id.id,
                        'qty': line_id.qty,
                        'uom_id': line_id.uom_id.id,
                        'maintenance_id': request_id.id,
                    }
                    self.env['equipment.part.line'].create(equipment_part_line_vals)
        return res

    @api.model
    def create(self, vals):
        if vals.get('wo_number', _('New')) == _('New'):
            vals['wo_number'] = self.env['ir.sequence'].next_by_code('maintenance.request') or _('New')

        request_id = super(HrEquipmentRequest, self).create(vals)

        if vals.get('equipment_id', False):

            equipment_data = self.env['maintenance.equipment'].browse(vals['equipment_id'])

            for check_id in equipment_data.check_ids:
                checklist_vals = {
                    'name': check_id.name,
                    'desc': check_id.desc,
                    'maintenance_id': request_id.id,
                }
                self.env['maintenance.checklist.line'].create(checklist_vals)
            for line_id in equipment_data.line_ids:
                equipment_part_line_vals = {
                    'product_id': line_id.product_id.id,
                    'qty': line_id.qty,
                    'uom_id': line_id.uom_id.id,
                    'maintenance_id': request_id.id,
                }
                self.env['equipment.part.line'].create(equipment_part_line_vals)
        return request_id

    # @api.model
    # def get_count_list(self):
    #     stage_data = self.env['maintenance.stage'].search([('name', '=', 'New Request')])
    #     request_data = self.env['maintenance.request'].search([('stage_id', '=', stage_data.id)]).ids
    #     calculate_stage = len(request_data)

    #     stage_first_approval = self.env['maintenance.stage'].search([('name', '=', 'First Approval')])
    #     request_first_approval = self.env['maintenance.request'].search([('stage_id', '=', stage_first_approval.id)]).ids
    #     calculate_first_approval = len(request_first_approval)

    #     stage_second_approval = self.env['maintenance.stage'].search([('name', '=', 'Second Approval')])
    #     request_second_approval = self.env['maintenance.request'].search([('stage_id', '=', stage_second_approval.id)]).ids
    #     calculate_second_approval = len(request_second_approval)

    #     stage_in_progress = self.env['maintenance.stage'].search([('name', '=', 'In Progress')])
    #     request_in_progress = self.env['maintenance.request'].search([('stage_id', '=', stage_in_progress.id)]).ids
    #     calculate_in_progress = len(request_in_progress)

    #     stage_in_repaired = self.env['maintenance.stage'].search([('name', '=', 'Repaired')])
    #     request_in_repaired = self.env['maintenance.request'].search([('stage_id', '=', stage_in_repaired.id)]).ids
    #     calculate_in_repaired = len(request_in_repaired)

    #     stage_in_scrap = self.env['maintenance.stage'].search([('name', '=', 'Scrap')])
    #     request_in_scrap = self.env['maintenance.request'].search([('stage_id', '=', stage_in_scrap.id)]).ids
    #     calculate_in_scrap = len(request_in_scrap)

    #     return {
    #         'calculate_stage': calculate_stage,
    #         'calculate_in_progress': calculate_in_progress,
    #         'calculate_first_approval': calculate_first_approval,
    #         'calculate_second_approval': calculate_second_approval,
    #         'calculate_in_repaired': calculate_in_repaired,
    #         'calculate_in_scrap': calculate_in_scrap,
    #     }

    @api.model
    def get_purchase_requision_data(self):
        cr = self._cr

        query = """
	       SELECT cl.request_date AS date_time,count(*) as count
	       FROM maintenance_request cl 
	       group by cl.request_date
	       order by cl.request_date
	       """
        cr.execute(query)
        partner_data = cr.dictfetchall()
        partner_day = []
        data_set = {}
        mycount = []
        list_value = []

        dict = {}
        count = 0

        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                  'August', 'September', 'October', 'November', 'December']

        for data in partner_data:
            if data['date_time']:
                mydate = data['date_time'].month
                for month_idx in range(0, 13):
                    if mydate == month_idx:
                        value = cal.month_name[month_idx]
                        list_value.append(value)
                        list_value1 = list(set(list_value))
                        for record in list_value1:
                            count = 0
                            for rec in list_value:
                                if rec == record:
                                    count = count + 1
                                dict.update({record: count})
                        keys, values = zip(*dict.items())
                        data_set.update({"data": dict})
        return data_set

