##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def write(self, values):     
        super(SaleOrderLine,self).write(values)

        self.order_id.sale_order_quote_log_ids.filtered(lambda x: x.log_type == 'descuento_componente_pack').unlink()

        for line in self:
            if line.order_id.state in ('draft','sent','sale'):
                if line.product_id.registrar_novedad_presupuesto:
                    # novedad: descuento en componente de pack
                    # import pdb; pdb.set_trace()
                    if line.pack_parent_line_id:
                        # es un componente de un pack
                        descuento_predefinido = line.pack_parent_line_id.product_id.pack_line_ids.filtered(lambda x: x.product_id.id == line.product_id.id).sale_discount 
                        descuento_modificado = line.discount                

                        if descuento_modificado > descuento_predefinido:                
                            self.env['sale.order.quote.log'].registrar_log(line.order_id,
                                "Descuento predefinido: {} - Descuento modificado: {}".format(
                                    descuento_predefinido,
                                    descuento_modificado),'descuento_componente_pack', line, line.product_id)