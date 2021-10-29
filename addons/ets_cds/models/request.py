from odoo import fields, models, api, _
from odoo import tools
from odoo.tools import html2plaintext
import base64



class CdsRequest(models.Model):
    """Заявки Диспетчерской службы"""

    _name = "cds.request"
    _description = "Заявки"

    name = fields.Char('Номер', copy=False, readonly=True, default=lambda x: _('New'))
    date = fields.Datetime(string='Дата', copy=False, readonly=True, default=fields.Datetime.now)

    user_id = fields.Many2one('res.users', copy=False, string='Пользователь', readonly=True, default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', copy=False, string='Сотрудник', related='user_id.partner_id')
    function = fields.Char('Должность', copy=False, related='partner_id.function')
    

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
    location_id = fields.Many2one('cds.location', string='Местонахождение', related='energy_complex_id.location_id')
    company_partner_id = fields.Many2one('res.partner', string='Заказчик', related='energy_complex_id.company_partner_id')
    object_id = fields.Many2one('cds.energy_complex_object', string='Объект')

    work_name = fields.Text('Наименование работ')
    
    description_mode = fields.Text("Режимные указания")

    total_load_gpes = fields.Char('Общая нагрузка ГПЭС')
    restrictions = fields.Char(string='Ограничения', default='нет')
    oil_losses = fields.Char(string='Потери нефти', default='нет')

    date_hand_over = fields.Datetime(string='Дата передачи', copy=False)

    state = fields.Selection(selection=[
            ('draft', 'Черновик'), 
            ('matching_in', 'Внутреннее согласование'), 
            ('matching_out', 'Согласование с заказчиком'), 
            ('agreed', 'Согласованно'), 
            ('failure', 'Отказано'), 
            ('open', 'Открыта'),
            ('close', 'Закрыта'),
            ('cancel', 'Отменена'),
        ], string="Статус", default='draft', required=True, copy=False,
    )

    date_turn_off = fields.Datetime(string='Отключение', copy=False)
    date_turn_on = fields.Datetime(string='Включение', copy=False)

    matching_ids = fields.One2many('cds.request_matching', 'request_id', string=u"Строки Согласующие")



    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('cds.request') or _('New')
        return super(CdsRequest, self).create(vals)

    @api.model
    def get_partner(self):
        if self.user_id:
            self.partner = self.user_id.partner_id



class CdsRequestMatching(models.Model):
    """Согласующие в Заявке Диспетчерской службы"""

    _name = "cds.request_matching"
    _description = "Согласующие"

    name = fields.Char("Наименование", compute="_get_name", store=True)
    partner_id = fields.Many2one('res.partner', string='Согласующий', domain="[('is_company', '=', False)]")
    function = fields.Char('Должность', related='partner_id.function')
    is_local = fields.Boolean(string='Внутренний согласующий', compute="_get_name", store=True)
    state = fields.Selection(selection=[
            ('matching', 'На согласовании'), 
            ('agreed', 'Согласованно'), 
            ('failure', 'Отказано'), 
        ], string="Статус", default='matching', required=True, copy=False, readonly=True
    )
    user_id = fields.Many2one('res.users', string='Согласовал', readonly=True, copy=False)
    date_state = fields.Datetime(string='Дата отметки', readonly=True, copy=False)


    request_id = fields.Many2one('cds.request', ondelete='cascade', string=u"Заявка", required=True)

    @api.depends("partner_id")
    def _get_name(self):
        if self.partner_id.parent_id:
            if self.partner_id.parent_id.is_company:
                if self.partner_id.parent_id.id == self.env.company.id:
                    self.is_local = True
                    self.name = self.partner_id.name + ", " + self.partner_id.function
                else:
                    self.is_local = False
                    self.name = self.partner_id.name
