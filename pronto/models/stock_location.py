from odoo import api, fields, models

class StockLocation(models.Model):
    _inherit = "stock.location"

    usuario_responsable_reserva_stock_id = fields.Many2one('res.users',string="Resp. reservas de stock")