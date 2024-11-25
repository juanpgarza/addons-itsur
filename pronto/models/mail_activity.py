
from odoo import api, exceptions, fields, models, _


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.depends('res_model', 'res_id')
    def _compute_res_url(self):
        for rec in self:
            rec.res_url = '/web#id=%s&model=%s' % (rec.res_id, rec.res_model)
    
    res_url = fields.Char(string='Url documento relacionado', help='Link al documento relacionado.', compute=_compute_res_url)

