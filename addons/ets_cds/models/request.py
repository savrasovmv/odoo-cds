from odoo import fields, models, api, _
from odoo import tools
from odoo.tools import html2plaintext
import base64


class CdsRequestState(models.Model):
    """Статусы Заявок Диспетчерской службы"""

    _name = "cds.request_state"
    _description = "Статусы"

    name = fields.Char('Наименование', copy=False, required=True)



class CdsRequest(models.Model):
    """Заявки Диспетчерской службы"""

    _name = "cds.request"
    _description = "Заявки"

    name = fields.Char('Номер', copy=False, readonly=True, default=lambda x: _('New'))
    date = fields.Datetime(string='Дата')

    mode = fields.Selection([
        ('plan', 'Плановая'),
        ('unplan', 'Внеплановая'),
        ('crash', 'Аварийная'),
    ], string='Вид', required=True)

    date_schedule = fields.Date(string='Дата по графику')
    ready_hours = fields.Integer("Аварийная готовность, часов")
    ready_minutes = fields.Integer("Аварийная готовность, минут")

    date_work_start = fields.Datetime(string='Дата начала работ')
    date_work_end = fields.Datetime(string='Дата окончания работ')

    energy_complex_id = fields.Many2one('cds.energy_complex', string='Энергокомплекс')
    location_id = fields.Many2one('cds.location', string='Местонахождение')
    object_id = fields.Many2one('cds.energy_complex_object', string='Объект')

    work_name = fields.Char('Наименование работ')
    
    description_mode = fields.Text("Режимные указания")

    total_load_gpes = fields.Char('Общая нагрузка ГПЭС')
    restrictions = fields.Char(string='Ограничения', default='нет')
    oil_losses = fields.Char(string='Потери нефти', default='нет')

    date_hand_over = fields.Datetime(string='Дата передачи')

    state = fields.Selection(selection=[
            ('draft', 'Черновик'), 
            ('matching_in', 'Внутреннее согласование'), 
            ('matching_out', 'Согласование с заказчиком'), 
            ('agreed', 'Согласованно'), 
            ('failure', 'Отказано'), 
            ('open', 'Открыта'),
            ('close', 'Закрыта'),
        ], string="Статус", default='draft', required=True,
    )

    date_turn_off = fields.Datetime(string='Отключение')
    date_turn_on = fields.Datetime(string='Включение')


    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('cds.request') or _('New')
        return super(CdsRequest, self).create(vals)

