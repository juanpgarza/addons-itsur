# -*- coding: utf-8 -*-
# Part of Odoo. See ICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

class ReturnPickingPronto(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _create_returns(self):

        in_out = self.picking_id.picking_type_id.code

        if in_out == 'outgoing':
            # se esta anulando una salida
            # recorro todos los renglones del wizard
            for return_picking_line in self.product_return_moves:
                if not return_picking_line.move_id:
                    raise UserError(_("You have manually created product lines, please delete them to proceed."))
                                
                cantidad_entregada = return_picking_line.move_id.sale_line_id.qty_delivered                
                cantidad_devuelve = return_picking_line.quantity
                product_id = return_picking_line.product_id
                if cantidad_devuelve > cantidad_entregada:
                    raise UserError(_("Cantidad devuelta({}) del producto \n {} \n es mayor a la cantidad entregada({}).".format(cantidad_devuelve,product_id.name,cantidad_entregada)))

        # else:
            # se esta anulando una entrada
            # import pdb; pdb.set_trace()

        # esta heredando desde stock_ux. ahí _create_returns retorna estos
        # dos valores. por eso se hace así
        new_picking, pick_type_id = super()._create_returns()

        return new_picking, pick_type_id
