##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta
import datetime
from odoo.exceptions import UserError, ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if not self.partner_id:
            # para que borre el "Entregar a" por defecto
            self.picking_type_id = False

    # picking_type_id = fields.Many2one(default=False)

    # No funciona!
    # @api.model
    # def _default_picking_type(self):
    #     import pdb; pdb.set_trace()
    #     return False
    
    # No funciona!
    # @api.model
    # def default_get(self, fields):
    #     rec = super(PurchaseOrder, self).default_get(fields)
    #     import pdb; pdb.set_trace()
    #     rec['picking_type_id'] = False

    #     return rec

    # No se esta usando? 06/03/2023
    # def actualizar_costos(self):
    #     net_price_installed = 'net_price' in self.env[
    #         'product.supplierinfo']._fields
    #     for rec in self.order_line.filtered('price_unit'):
    #         producto = self.env['product.product'].browse([rec.product_id.id])
    #         producto.update({'standard_price': rec.price_unit})

    # No se esta usando? 06/03/2023
    # @api.model
    # def control_fecha_recepcion(self):
    #     purchase_order = self.env["purchase.order"].search([('state','=','purchase')])

    #     # cant. de días antes de la fecha prevista para registrar la actividad
    #     dias_registrar_actividad = 2
    #     activity_type_id = self.env.ref('pronto.confirmar_fecha_recepcion')
    #     model_stock_picking = self.env.ref('purchase.model_purchase_order')

    #     for po in purchase_order:
    #         for pol in po.order_line:
    #             # todavía queda pendientes
    #             if pol.product_qty != pol.qty_received:
    #                 # delta = picking.scheduled_date.date() - fields.Date.context_today(self)
    #                 delta = pol.date_planned.date() - fields.Date.context_today(self)
    #                 if delta.days == dias_registrar_actividad or delta.days <= 0:

    #                     summary = activity_type_id.summary + ' - ' + str(pol.product_id.default_code)
    #                     res_id = pol.order_id.id
                        
    #                     # verficar si tiene actividad de ese tipo
    #                     activity = self.env['mail.activity'].search([('res_model_id','=',model_stock_picking.id),
    #                     ('activity_type_id','=',activity_type_id.id),
    #                     ('res_id','=',res_id),
    #                     ('summary','=',summary),])
                        
    #                     if not activity:
    #                         # self._schedule_activity(activity_type_id, pol.order_id, pol.product_id)
    #                         vals = {
    #                             'activity_type_id': activity_type_id.id,
    #                             'date_deadline': fields.Date.today(),
    #                             'summary': summary,
    #                             'user_id': 8, # marcos
    #                             'res_id': res_id,
    #                             'res_model_id': model_stock_picking.id,
    #                             'res_model':  model_stock_picking.model
    #                         }
    #                         # mail_activity_quick_update=True para que no le muestre un aviso al usuario. t-70
    #                         self.env['mail.activity'].with_context(mail_activity_quick_update=True).create(vals)

    def write(self, values):
        # import pdb; pdb.set_trace()
        if self.user_has_groups('pronto.group_compras_solo_lectura_ordenes_compra'):
            raise ValidationError("Su usuario solo está habilitado para escribir en el chatter ")
        super(PurchaseOrder,self).write(values)