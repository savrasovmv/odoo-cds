from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # 1С
    department_id = fields.Many2one('cds.department', string='Подразделение')
    print_name = fields.Char(string='ФИО для печати', store=True, compute="_get_print_name")

    @api.depends('name')
    def _get_print_name(self):
        for rec in self:
            fio = rec.name.split(' ')
            if len(fio)>1:
                if len(fio)==2:
                    rec.print_name = fio[1][0] + '. ' + fio[0] 
                if len(fio)==3:
                    rec.print_name = fio[1][0] + '.' + fio[2][0] + '. ' + fio[0]
            else:
                rec.print_name = rec.name