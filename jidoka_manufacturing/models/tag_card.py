from odoo import _, api, fields, models

class TagCard(models.Model):
    _name = 'tag.card'
    _description = 'Tag Card'
    
    name = fields.Char('No Tag')
    prod_intruction_id = fields.Many2one('mrp.production', string='Prod Intruction')
    bahan = fields.Selection([
        ('baku', 'Baku'),
        ('setengah_jadi', 'Setengah Jadi'),
        ('kd', 'K/D'),
        ('sertifikat', 'Bersertifikat'),
        ('moulding', 'Moulding'),
        ('ad', 'A/D'),
        ('tidak', 'Tidak'),
    ], string='Bahan', default='baku')
    fisik = fields.Selection([
        ('standard', 'Standard'),
        ('tipis', 'Tipis'),
        ('mata', 'Mata'),
    ], string='Fisik', default='standard')
    kode_beli = fields.Char('Kode Beli')
    kualitas = fields.Char('Kualitas')
    stage = fields.Char('Proses')
    marking = fields.Char('Marking')
    tgl_masuk = fields.Date('Tgl Masuk', required=True)
    jenis_kayu = fields.Selection([
        ('jati', 'Jati'),
        ('non_jati', 'Non Jati'),
    ], string='jenis_kayu', default='jati')
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    total_pcs = fields.Float('Total Pcs')
    total_m3 = fields.Float('Total M3', digits=(12,6))
    location_id = fields.Many2one('stock.location', string='Location', required=True)
    it = fields.Char('IT')
    card_line_ids = fields.One2many('tag.card.line', 'tag_card_id', string='Card Line')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    note = fields.Text('Keterangan')
    
class TagCardLine(models.Model):
    _name = 'tag.card.line'
    _description = 'Tag Card Line'
    
    name = fields.Char('Part Name')
    tag_card_id = fields.Many2one('tag.card', string='Tag Card', ondelete="cascade")
    ukuran = fields.Float(string="Item No/Ukuran")
    quantity = fields.Float('PCS')
    uom_id = fields.Many2one('uom.uom', string='Uom')
    volume = fields.Float('M3')
    note = fields.Text('Keterangan')
    production_id = fields.Many2one('mrp.production', string='Production')