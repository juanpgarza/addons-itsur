from odoo import api, models, fields
from odoo.exceptions import ValidationError
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_due = fields.Monetary(
        related='partner_id.total_due',
        string = 'Saldo'
    )

    weight = fields.Float(compute='_compute_weight', string='Peso total', readonly=True, store=True)
    weight_uom_name = fields.Char(string='Unidad de peso', compute='_compute_weight_uom_name')

    cotizacion = fields.Float(string='Cotización',
                            compute='_compute_cotizacion', 
                            store=True,
                            help='Cotización del dolar en la fecha del presupuesto/pedido.')

    sale_order_reference = fields.Char("Referencia")

    @api.depends('order_line.product_uom_qty')
    def _compute_weight(self):
        for order in self:            
            # tomé como ejemplo: https://github.com/OCA/sale-reporting/blob/14.0/sale_order_weight/models/sale_order_line.py
            lines_weight = 0.0
            # filtro los que no son productos (secciones / notas)
            for line in order.order_line.filtered(lambda x: not x.display_type):
                if line.product_id:
                    lines_weight += line.product_id.weight * line.product_uom_qty
            order.update({
                'weight': lines_weight,
            })

    def _compute_weight_uom_name(self):
        weight_uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        for order in self:
            order.weight_uom_name = weight_uom_id.name

    @api.depends('date_order')
    def _compute_cotizacion(self):
        for order in self:
            moneda_origen = self.env.ref('base.USD')
            moneda_destino = self.env.ref('base.ARS')
            compania = self.env.user.company_id
            order.cotizacion = moneda_origen._convert(1,moneda_destino,compania, order.date_order)

    def write(self, values):
        if self.user_has_groups('pronto.group_commitment_date_required'):
            if ('state' in values and self.state != 'done' and values['state'] == 'sale') or 'user_requesting_review' in values:
                    if not self.commitment_date:
                        raise ValidationError(
                                'Debe informar la fecha de compromiso'
                                )

        if self.user_has_groups('pronto.group_ventas_solo_lectura_pedidos'):
            raise ValidationError("Su usuario solo está habilitado para escribir en el chatter ")        
        return super(SaleOrder, self).write(values)
