##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError
# import odoo.addons.decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_order_type_id = fields.Many2one(related="sale_id.type_id", string= 'Tipo de venta')
    
    @api.model
    def _schedule_activity(self,activity_type_id):

        model_stock_picking = self.env.ref('stock.model_stock_picking')
        if self.location_id.usuario_responsable_reserva_stock_id:
            asignada_a = self.location_id.usuario_responsable_reserva_stock_id 
        else:
            asignada_a = self.env.user.company_id.usuario_responsable_reserva_stock_id

        vals = {
            'activity_type_id': activity_type_id.id,
            'date_deadline': fields.Date.today(),
            'summary': activity_type_id.summary,
            'user_id': asignada_a.id,
            'res_id': self.id,
            'res_model_id': model_stock_picking.id,
            'res_model':  model_stock_picking.model
        }
        # mail_activity_quick_update=True para que no le muestre un aviso al usuario. t-70
        return self.env['mail.activity'].with_context(mail_activity_quick_update=True).create(vals)


    def button_validate(self):
        # solo en los movimientos de salida
        if (self.picking_type_id.code == 'outgoing'):
            # Control de productos agregados al pedido pero que no se facturaron
            if not self.user_has_groups('pronto.group_stock_omitir_bloqueo_pendiente_facturar'):
                if self.sale_id.order_line.filtered(lambda x: x.qty_invoiced < x.product_uom_qty):
                    raise UserError("El pedido asociado al movimiento tiene productos pendientes de facturar.")

        result = super(StockPicking,self).button_validate()
        # solo en los movimientos de salida
        if (self.picking_type_id.code == 'outgoing'):
            # solo si tienen facturas asociadas.
            # osea que para tipo de venta 'sin factura' no aplica porque no se le asocia factura al movimiento
            # tampoco para las transferencia internas porque las operaciones son del tipo 'internal'
            for inv in self.invoice_ids:
                if (inv.move_type == 'out_invoice'):
                    # solo para las facturas (sin NC)
                    if (inv.state == 'draft'):
                        raise UserError("Este movimiento tiene al menos una factura asociada en estado borrador.")
        
        return result

    def do_print_voucher(self):
        # import pdb; pdb.set_trace()
        '''This function prints the voucher'''
        report = self.env['ir.actions.report'].search(
            [('report_name', '=', 'pronto.report_picking')],
            limit=1).report_action(self)
        return report

    def assign_numbers(self, estimated_number_of_pages, book):
        result = super(StockPicking,self).assign_numbers(estimated_number_of_pages, book)

        cantidad_renglones = self.env['stock.book'].browse(self.book_id.id).lines_per_voucher

        if (cantidad_renglones == 0):
            raise UserError("Debe configurar la cantidad de renglones para el talonario.")

        vouchers = self.env['stock.picking.voucher'].search([('picking_id','=',self.id)])

        for voucher in vouchers:
            # movimientos que todavía no tienen remitos asignados
            moves = self.env['stock.move'].search(['&',('picking_id','=',self.id),('picking_voucher_id','=',False)])
            renglon = 0
            for move in moves.filtered(lambda x: x.quantity_done):
                move.write({'picking_voucher_id': voucher.id})
                renglon = renglon + 1
                if renglon >= cantidad_renglones:
                    break
            
        return result

    def clean_voucher_data(self):
        moves = self.env['stock.move'].search([('picking_id','=',self.id)])
        for move in moves:
            move.picking_voucher_id = None
        result = super(StockPicking,self).clean_voucher_data()