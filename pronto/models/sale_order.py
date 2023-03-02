from odoo import api, models, fields
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_due = fields.Monetary(
        related='partner_id.total_due',
        string = 'Saldo'
    )

    weight = fields.Float(compute='_compute_weight', string='Peso total', readonly=True, store=True)
    weight_uom_name = fields.Char(string='Unidad de peso', compute='_compute_weight_uom_name')
    
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