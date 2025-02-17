##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from datetime import timedelta
import logging
_logger = logging.getLogger(__name__)

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    fixed_price = fields.Float(digits=('Pricelist Fixed Price'))

    @api.model
    def _controlar_actualizacion_tarifa_costo(self):
        cost_pricelist_id = self.env.user.company_id.product_pricelist_cost_id
        dias_costo_sin_actualizar_sistema = int(self.env['ir.config_parameter'].get_param('pronto.dias_costo_sin_actualizar'))
        
        activity_type_id = self.env.ref('pronto.actualizar_costo')
        asignada_a = self.env.user.company_id.usuario_responsable_actualizacion_costo_id
        model_product_pricelist_item = self.env.ref('product.model_product_pricelist_item')
        mail_activity = self.env['mail.activity'].with_context(mail_activity_quick_update=True)

        if not asignada_a:
            _logger.error("Debe informar el responsable de actualizar costos.")
            return

        fecha_actual = fields.Date.context_today(self)
        _logger.info("Iniciando control de actualización de tarifa de costo.")
        actividades = 0
        for item in cost_pricelist_id.item_ids:

            if item.product_tmpl_id.dias_costo_sin_actualizar:
                dias_costo_sin_actualizar = item.product_tmpl_id.dias_costo_sin_actualizar
            else:
                dias_costo_sin_actualizar = dias_costo_sin_actualizar_sistema            
            
            if item.fecha_ultima_modificacion_precio: 
                delta_modificacion = fecha_actual - item.fecha_ultima_modificacion_precio
            else:
                delta_modificacion = timedelta(days=dias_costo_sin_actualizar+1)

            if item.fecha_ultimo_control:
                delta_control = fecha_actual - item.fecha_ultimo_control
            else:
                delta_control = timedelta(days=dias_costo_sin_actualizar+1)
            
            # import pdb; pdb.set_trace()
            if delta_modificacion.days >= dias_costo_sin_actualizar and delta_control.days >= dias_costo_sin_actualizar:
                # import pdb; pdb.set_trace()
                existe_actividad = self.env['mail.activity'].search([('res_model_id','=',model_product_pricelist_item.id),
                        ('activity_type_id','=',activity_type_id.id),
                        ('res_id','=',item.id)])

                if not existe_actividad:

                    vals = {
                        'activity_type_id': activity_type_id.id,
                        'date_deadline': fields.Date.today(),
                        'summary': activity_type_id.summary,
                        'user_id': asignada_a.id,
                        'res_id': item.id,
                        'res_model_id': model_product_pricelist_item.id,
                        'res_model':  model_product_pricelist_item.model
                    }
                    # mail_activity_quick_update=True para que no le muestre un aviso al usuario. t-70
                    mail_activity.create(vals)
                    actividades += 1

        _logger.info("Se generaron %d actividades.", actividades)

    def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
        res = super(ProductPricelist, self)._compute_price_rule(products_qty_partner,date,uom_id)
        # import pdb; pdb.set_trace()
        return res    