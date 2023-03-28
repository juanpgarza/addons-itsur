from odoo import fields, models, api

class SaleOrderQuoteLog(models.Model):
    _name = 'sale.order.quote.log'
    _description = 'Logs de presupuestos'

    sale_order_id = fields.Many2one('sale.order',string="Pedido")
    order_line_id = fields.Many2one('sale.order.line',string="Línea de Pedido")
    fecha_hora = fields.Datetime(string="Fecha Log")
    description = fields.Char(string="Descripción")
    product_id = fields.Many2one('product.product')
    log_type = fields.Selection(
                            [('validez','Fecha Validez'),
                            ('precio','Precio'),
                            ('descuento_componente_pack','Descuento en componente de pack'),
                            ('otro','Otro')
                            ],'Tipo')

    @api.model
    def registrar_log(self, order_id, description, log_type, order_line_id = None, product_id = None):

        vals = {
            'sale_order_id': order_id.id,
            'fecha_hora': fields.Datetime.now(),
            'description': description,
            'log_type': log_type
        }

        if product_id:
            vals['product_id'] = product_id.id

        if order_line_id:
            vals['order_line_id'] = order_line_id.id            
        
        log = self.env['sale.order.quote.log'].create(vals)
    