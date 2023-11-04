from odoo import _, fields, api, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_qc = fields.Boolean('Is QC?', default=True, compute="get_is_qc")
    # qc_state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('check', 'Checking'),
    #     ('confirm', 'Confirm'),
    #     ('reject', 'Rejected'),
    #     ('done', 'Done'),
    # ], string="QC State", 
    #     compute='_compute_state_qc' )
    
    # @api.depends('move_ids_without_package')
    # def _compute_state_qc(self):
    #     stock_move = self.move_ids_without_package
    #     for sm in stock_move[0]:
    #         self.qc_state = sm.search([('picking_id','=',self.id),('qc_state','=','done')]).qc_state
    
    qc_state_done = fields.Boolean('QC State Done', 
        compute='_compute_qc_state_done' )
    
    @api.depends('move_ids_without_package')
    def _compute_qc_state_done(self):
        for r in self:
            count_qc_state = len(r.move_ids_without_package.search([('picking_id','=',self.id)]).mapped('qc_state'))
            count_qc_state_done = len(r.move_ids_without_package.search([('picking_id','=',self.id),('qc_state','=','done')]).mapped('qc_state'))
            if count_qc_state == count_qc_state_done:
                r.qc_state_done = True
            else:
                r.qc_state_done = False
    
    
    
            
    # count_qc_state = fields.Integer('Count QC State', 
    #     compute='_compute_count_qc_state',store=True )
    
    # @api.depends('move_ids_without_package')
    # def _compute_count_qc_state(self):
    #     # for stock_move in self.move_ids_without_package:
    #     #     self.count_qc_state = len(stock_move.search([('picking_id','=',self.id)]).mapped('qc_state'))
    #     self.count_qc_state = len(self.move_ids_without_package.search([('picking_id','=',self.id)]).qc_state)
            
    # count_qc_state_done = fields.Integer('Count QC State Done', 
    #     compute='_compute_count_qc_state_done',store=True )
    
    # @api.depends('move_ids_without_package')
    # def _compute_count_qc_state_done(self):
    #     # for stock_move in self.move_ids_without_package:
    #     #     self.count_qc_state_done = len(stock_move.search([('picking_id','=',self.id),('qc_state','=','done')]).mapped('qc_state'))
        
    #     self.count_qc_state_done = len(self.move_ids_without_package.search([('picking_id','=',self.id),('qc_state','=','done')]).mapped('qc_state'))
    
    
    
    
    # self.move_ids_without_package.search([('picking_id','=',self.id),('qc_state','=','done')])
    # self.move_ids_without_package.search([('picking_id','=',self.id),('qc_state','=','done')]).qc_state
    # quantity_qc_state_done = len(self.move_ids_without_package.search([('picking_id','=',self.id),('qc_state','=','done')]).mapped('qc_state'))
    
    # self.env[‘res.partner’].search_count([(‘name’, ‘ilike’, ‘muhammad’), (‘city’, ‘=’, ‘bekasi’)])
    
    # self.move_ids_without_package.search_count([('picking_id','=',self.id),('qc_state','=','done')])


    
    # quantity_qc_state = len(self.move_ids_without_package.search([('picking_id','=',self.id)]).mapped('qc_state'))
    
    # self.move_ids_without_package.search([('picking_id','=',self.id),('qc_state','=','done')])
    
    
    
    

    @api.depends('move_ids_without_package.qc_state')
    def get_is_qc(self):
        """Flagging for hide button Validate"""
        self.is_qc = True
        for rec in self.move_ids_without_package:
            if rec.picking_id.picking_type_code != 'internal' and  rec.qc_state != 'done' and rec.product_id.wood_type == 'timber':
                rec.picking_id.is_qc = False
                

class StockMove(models.Model):
    _inherit = 'stock.move'

    qc_state = fields.Selection([
        ('draft', 'Draft'),
        ('check', 'Checking'),
        ('confirm', 'Confirm'),
        ('reject', 'Rejected'),
        ('done', 'Done'),
    ], related="qc_id.state", string="QC State")
    qc_id = fields.Many2one('quality.check', string='QC',)

    def prepare_quality_check(self):
        vals = {
            'product_id' : self.product_id.id,
            'quantity_received' : self.product_uom_qty,
            'supplier_id' : self.purchase_line_id.order_id.partner_id.id if self.purchase_line_id else False,
            'buyer_id' : self.purchase_line_id.order_id.user_id.id if self.purchase_line_id else False,
            'move_id' : self.id,
            'picking_id' : self.picking_id.id,
        }
        return vals

    def action_view_qc(self):
        action = self.env["ir.actions.actions"]._for_xml_id("qa_qc.quality_check_action")
        return action
    
    wood_type = fields.Selection([
        ('log', 'LOG'),
        ('square', 'Square Log'),
        ('timber', 'Sawn Timber')
    ], string='Type', related='product_id.wood_type', store=True)

    def button_qc(self):
        # import pdb;pdb.set_trace()
        """Automatically in to QC Form"""
        action = self.action_view_qc()
        if not self.qc_id :
            vals = self.prepare_quality_check()
            quality_check_id = self.env['quality.check'].create(vals)
            if quality_check_id:
                self.write({
                    'qc_id' : quality_check_id.id,
                })
            
            action['res_id'] = quality_check_id.id
        else:
            action['res_id'] = self.qc_id.id
        action['views'] = [(self.env.ref('qa_qc.quality_check_view_form').id, 'form')]
        return action

