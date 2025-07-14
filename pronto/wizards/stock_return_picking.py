##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import UserError

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    reason_id = fields.Many2one(comodel_name="stock.return.picking.reason", string= 'Motivo de devolución')

    def _create_return(self):
        # add to new picking for return the reason for the return
        new_picking = super()._create_return()
        # picking = self.env['stock.picking'].browse(new_picking)
        new_picking.write({'reason_id': self.reason_id.id})

        return new_picking
