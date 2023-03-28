##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import _, api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_order_quote_log_ids = fields.One2many('sale.order.quote.log','sale_order_id',string="Logs del pedido", copy=False)

    def write(self, values):     
        super(SaleOrder,self).write(values)
        
        if self.state in ('draft','sent','sale'):
            self.sale_order_quote_log_ids.filtered(lambda x: x.log_type in ('validez', 'precio')).unlink()

            delta = self.validity_date - fields.Date.context_today(self)

            if delta.days < 0:
                self.env['sale.order.quote.log'].registrar_log(self, "Fecha de validez vencida: {}".format(self.validity_date),'validez')

            for line in self.order_line.filtered(lambda x: not x.display_type):
                if line.product_id.registrar_novedad_presupuesto:
                    # novedad: descuento en componente de pack
                    if line.pack_parent_line_id:
                        # es un componente de un pack
                        descuento_predefinido = line.pack_parent_line_id.product_id.pack_line_ids.filtered(lambda x: x.product_id.id == line.product_id.id).sale_discount 
                        descuento_modificado = line.discount

                        if descuento_modificado > descuento_predefinido:                
                            self.env['sale.order.quote.log'].registrar_log(self,
                                "Descuento predefinido: {} - Descuento modificado: {}".format(
                                    descuento_predefinido,
                                    descuento_modificado),'descuento_componente_pack', line, line.product_id)

                    if line.pack_parent_line_id and line.pack_parent_line_id.pack_type == 'detailed' and line.pack_parent_line_id.pack_component_price == 'totalized':
                        # el precio de los componentes están siempre en cero. No se controla la novedad de precios.
                        continue

                    # copiado desde: product_uom_change (addons/sale)
                    if line.order_id.pricelist_id and line.order_id.partner_id:                        
                        product = line.product_id.with_context(
                            lang=line.order_id.partner_id.lang,
                            partner=line.order_id.partner_id,
                            quantity=line.product_uom_qty,
                            # date=line.order_id.date_order,
                            date=fields.Datetime.now(),
                            pricelist=line.order_id.pricelist_id.id,
                            uom=line.product_uom.id,
                            fiscal_position=line.env.context.get('fiscal_position')
                        )
                        precio_unitario_actual = round(self.env['account.tax']._fix_tax_included_price_company(line._get_display_price(product), product.taxes_id, line.tax_id, line.company_id),2)

                        precio_unitario = round(line.price_unit,2)

                        if precio_unitario != precio_unitario_actual:                
                            self.env['sale.order.quote.log'].registrar_log(self,
                                "Precio anterior: {} - Precio nuevo: {}".format(
                                    precio_unitario,
                                    precio_unitario_actual),'precio', line, product)                    

                    
        return