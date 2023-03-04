##############################################################################
# For copyright and license notices, see __manifest__.py file in module root
# directory
##############################################################################
from odoo import fields, models, api, _
from odoo.exceptions import UserError
# import odoo.addons.decimal_precision as dp


class ProntoStockPicking(models.Model):
    _inherit = 'stock.picking'

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

