from odoo import tools
from odoo import api, fields, models


class SaleReportPronto(models.Model):
    _name = "sale.report.pronto"
    _description = "Sales Analysis Report PRONTO"
    _auto = False
    _rec_name = 'name'
    _order = 'id desc'

    @api.model
    def _get_done_states(self):
        return ['sale', 'done', 'paid']

    name = fields.Char('Número de pedido', readonly=True)
    date = fields.Datetime('Fecha de pedido', readonly=True)
    product_id = fields.Many2one('product.product', 'Producto', readonly=True)
    product_uom_qty = fields.Float('Cant. pedida', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Plantilla de producto', readonly=True)
    categ_id = fields.Many2one('product.category', 'Categoría', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Tarifa', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Sales Done'),
        ('cancel', 'Cancelled'),
        ], string='Estado', readonly=True)
    discount = fields.Float('% Descuento', readonly=True)

    order_id = fields.Many2one('sale.order', '# Pedido', readonly=True)
    line_id = fields.Many2one('sale.order.line', '# Linea', readonly=True)

    porcentaje = fields.Float('Porcentaje', readonly=True, group_operator='avg')
    
    cotizacion = fields.Float('Cotización USD', readonly=True, group_operator='avg')
    costo_total_pesos = fields.Float('Costo total en pesos', readonly=True)
    precio_total_pesos = fields.Float('Precio total en pesos', readonly=True)
    margin = fields.Float('Margen', readonly=True)
    precio_total_usd = fields.Float('Precio total en USD', readonly=True)

    tag_ids = fields.Many2many(related="order_id.tag_ids",string = "Etiquetas")
    
    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        with_ = ("WITH %s" % with_clause) if with_clause else ""

        select_ = """
            l.id as id,
            l.product_id as product_id,
            t.uom_id as product_uom,
            l.product_uom_qty as product_uom_qty,
            s.name as name,
            s.date_order as date,
            s.state as state,
            s.partner_id as partner_id,
            s.user_id as user_id,
            s.company_id as company_id,
            t.categ_id as categ_id,
            s.pricelist_id as pricelist_id,
            s.analytic_account_id as analytic_account_id,
            s.team_id as team_id,
            p.product_tmpl_id,
            partner.country_id as country_id,
            partner.commercial_partner_id as commercial_partner_id,
            l.discount as discount,
            s.id as order_id, 
            l.id as line_id,
            s.cotizacion as cotizacion,
            l.costo_total_pesos as costo_total_pesos, 
            l.precio_total_pesos as precio_total_pesos,
            l.precio_total_pesos - l.costo_total_pesos as margin,
            l.precio_total_pesos / nullif(s.cotizacion,0) as precio_total_usd,
            CASE WHEN l.costo_total_pesos > 0 and l.precio_total_pesos > 0 THEN  (l.precio_total_pesos / l.costo_total_pesos - 1) * 100 ELSE 0 END as porcentaje
        """

        for field in fields.values():
            select_ += field

        from_ = """
                sale_order_line l
                      join sale_order s on (l.order_id=s.id)
                      join res_partner partner on s.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join uom_uom u on (u.id=l.product_uom)
                    left join uom_uom u2 on (u2.id=t.uom_id)
                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                %s
        """ % from_clause

        return '%s (SELECT %s FROM %s WHERE l.product_id IS NOT NULL AND NOT l.excluir_markup)' % (with_, select_, from_)

    def init(self):
        # self._table = sale_report
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))