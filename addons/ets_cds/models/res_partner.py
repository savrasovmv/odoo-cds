from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # 1С
    department_id = fields.Many2one('cds.department', string='Подразделение')