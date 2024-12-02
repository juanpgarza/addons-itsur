from odoo import api, models, fields
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    costo_total_pesos = fields.Float(string = 'Costo total pesos', compute='_computed_costo_total_pesos', readonly=False, store=True)
    precio_total_pesos = fields.Float(string = 'Precio total pesos', compute='_computed_precio_total_pesos', readonly=False, store=True, copy=False)

    excluir_markup = fields.Boolean(string="Excluir del calculo del mark-up (Porcentaje) en los pedidos",
                    compute='_computed_excluir_markup', 
                    readonly=False, 
                    store=True)
    
    @api.depends('product_id','product_id.excluir_calculo_markup')
    def _computed_excluir_markup(self):
        for rec in self:
            if rec.product_id.excluir_calculo_markup == 'siempre':                
                rec.excluir_markup = True
            elif rec.product_id.excluir_calculo_markup == 'componente_pack':
                if rec.pack_parent_line_id:
                    rec.excluir_markup = True
            else:
                rec.excluir_markup = False

    @api.depends('product_id', 'product_uom_qty','purchase_price')
    def _computed_costo_total_pesos(self):
        # import pdb; pdb.set_trace()

        for rec in self:        
            if rec.display_type:
                # es una sección
                continue

            costo_total_pesos = rec.product_uom_qty * rec.purchase_price
            if rec.order_id.pricelist_id.currency_id != rec.env.user.company_id.currency_id:
                rec.costo_total_pesos = costo_total_pesos * rec.order_id.cotizacion
            else:
                rec.costo_total_pesos = costo_total_pesos

    @api.depends('product_id', 'product_uom_qty','purchase_price', 'price_unit', 'order_id.pricelist_id', 'discount')    
    def _computed_precio_total_pesos(self,precio_total=False):
        # se llama desde lo módulo clima
        # clima es el que determina el precio_total (sin desc. clima)
        
        for rec in self:
            if rec.display_type:
                # es una sección
                continue
            
            if precio_total:
                precio_total_pesos = precio_total
            else:
                precio_total_pesos = rec.price_subtotal
                
            # precio_total_pesos = rec.product_uom_qty * rec.price_unit
            if rec.order_id.pricelist_id.currency_id != rec.env.user.company_id.currency_id:
                rec.precio_total_pesos = precio_total_pesos * rec.order_id.cotizacion
            else:
                rec.precio_total_pesos = precio_total_pesos
    
            if rec.product_id.pack_ok and rec.product_id.pack_type == 'detailed' and rec.product_id.pack_component_price == 'detailed':
                # el precio_total_pesos está en los componentes del pack
                rec.precio_total_pesos = 0

    # @api.depends('price_subtotal', 'product_uom_qty', 'purchase_price')
    # def _compute_margin(self):
    #     super(SaleOrderLine,self)._compute_margin()
    #     for line in self:
    #         if line.excluir_markup:
    #             line.margin = 0
    #             line.margin_percent = 0
            # else:
            #     line.margin = line.price_subtotal - (line.purchase_price * line.product_uom_qty)
            #     line.margin_percent = line.price_subtotal and line.margin/line.price_subtotal

        # src/addons/sale_margin/models/sale_order.py:29
        # for line in self:
        #     line.margin = line.price_subtotal - (line.purchase_price * line.product_uom_qty)
        #     line.margin_percent = line.price_subtotal and line.margin/line.price_subtotal

    @api.depends('product_id', 'company_id', 'currency_id', 'product_uom')
    def _compute_purchase_price(self):
        super(SaleOrderLine,self)._compute_purchase_price()
        # esto se necesita porque sino al hacer "Actualizar precios" el costo queda en cero
        # pero no funciona cuando cambia el producto porque las lineas del los packs recien se generan al guardar
        # import pdb; pdb.set_trace()
        for line in self:
            # import pdb; pdb.set_trace()
            if line.product_id.pack_ok and line.product_id.pack_component_price == 'totalized':
                line._compute_purchase_price_totalized_pack()

        # src/addons/sale_margin/models/sale_order.py:20
        # for line in self:
        #     if not line.product_id:
        #         line.purchase_price = 0.0
        #         continue
        #     line = line.with_company(line.company_id)
        #     product_cost = line.product_id.standard_price
        #     line.purchase_price = line._convert_price(product_cost, line.product_id.uom_id)

    @api.model_create_multi
    def create(self,values):
        line = super(SaleOrderLine,self).create(values)
        if line.product_id.pack_ok and line.product_id.pack_component_price == 'totalized':
            line._compute_purchase_price_totalized_pack()
            # import pdb; pdb.set_trace()
            # total_purchase_price = 0
            # for subline in line.pack_child_line_ids:
            #     product_cost = subline.product_id.standard_price
            #     total_purchase_price += subline._convert_price(product_cost, subline.product_id.uom_id)
            # line.purchase_price = total_purchase_price
        return line

    # def write(self, values):
    #     super(SaleOrderLine,self).write(values)
    #     for line in self:
    #         if line.product_id.pack_ok and line.product_id.pack_component_price == 'totalized':
                # import pdb; pdb.set_trace()

    
    def _compute_purchase_price_totalized_pack(self):
        for line in self:
            total_purchase_price = 0
            for subline in line.pack_child_line_ids:
                product_cost = subline.product_id.standard_price
                total_purchase_price += subline._convert_price(product_cost, subline.product_id.uom_id)
            line.purchase_price = total_purchase_price