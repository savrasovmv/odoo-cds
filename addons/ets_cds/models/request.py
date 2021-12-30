from odoo import fields, models, api, _
from odoo import tools
from odoo.tools import html2plaintext
import base64
from datetime import datetime



class CdsRequest(models.Model):
    """Заявки Диспетчерской службы"""

    _name = "cds.request"
    _description = "Заявки"

    name = fields.Char('Номер', copy=False, readonly=True, default=lambda x: _('New'))
    date = fields.Datetime(string='Дата', copy=False, readonly=True, default=fields.Datetime.now)

    user_id = fields.Many2one('res.users', copy=False, string='Пользователь', readonly=True, default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', copy=False, string='Сотрудник', related='user_id.partner_id', store=True)
    function = fields.Char('Должность', copy=False, related='partner_id.function', store=True)
    

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
    location_id = fields.Many2one('cds.location', string='Местонахождение', related='energy_complex_id.location_id', store=True)
    company_partner_id = fields.Many2one('res.partner', string='Заказчик', related='energy_complex_id.company_partner_id', store=True)
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
            ('agreed', 'Согласовано'), 
            ('failure', 'Не согласовано'), 
            ('open', 'Открыта'),
            ('extend', 'Продлена'),
            ('close', 'Закрыта'),
            ('cancel', 'Отменена'),
        ],
        group_expand='_expand_groups',
        string="Статус", 
        default='draft', 
        required=True, 
        copy=False,
    )

    date_turn_off = fields.Datetime(string='Отключение', copy=False)
    date_turn_on = fields.Datetime(string='Включение', copy=False)

    description_partner = fields.Text("Комментарий для заказчика")
    description = fields.Text("Комментарии к заявке")

    attachment_ids = fields.Many2many('ir.attachment', 'cds_request_ir_attachments_rel',
        'request_id', 'attachment_id', string='Вложения')


    matching_ids = fields.One2many('cds.request_matching', 'request_id', string=u"Строки Согласующие")

    is_action_state = fields.Boolean(string='Действия для пользователя', compute="_get_action_state_user", help="Признак тредуется ли действие от пользователя на текущем сттусе заявки, True - действие требуется, False - действий не требуется")

    action_state = fields.Char(string='Состояние', compute="_get_action_state", help="Текстовое описание состояния в текущем статусе")

    @api.model
    def _expand_groups(self, states, domain, order):
        return ['draft', 'matching_in', 'matching_out', 'agreed', 'open', 'extend', 'failure', 'close', 'cancel']


    @api.model
    def create(self, vals):
        if not vals.get('name') or vals['name'] == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('cds.request') or _('New')
        return super(CdsRequest, self).create(vals)

    @api.model
    def get_partner(self):
        if self.user_id:
            self.partner = self.user_id.partner_id

    def action_set_request_matching(self):
        """Заполнить согласующих из шаблона Энергокомплекса"""
        self.matching_ids.unlink()

        for line in self.energy_complex_id.matching_ids:
            self.env['cds.request_matching'].create({
                'request_id': self.id,
                'partner_id': line.partner_id.id,
            })


    def random_value(self):
        from random import randint
        value = randint(10, 40)
        return value

    def _get_action_state(self):
        self.ensure_one()
        self.action_state = self.state

        if self.state == 'draft':
            self.action_state = "Черновик. Нажмите Начать, что бы зпустить процесс согласования"
        if self.state == 'matching_in':
            count = self.env['cds.request_matching'].search_count([
                ('request_id', '=', self.id),
                ('is_local', '=', True),
                ('state', '=', 'matching'),
                ('user_id', '=', False),
            ])
            if count>0: 
                self.action_state = "Ожидает согласования от %s пользователей" % (count)
            else:
                self.action_state = "Внутреннее согласование завершено. Необходимо перейти к следующему этапу"




    def _get_action_state_user(self):
        self.ensure_one()
        self.is_action_state = False
        user = self.env.user
        partner_id = user.partner_id
        if self.state == 'matching_in' or self.state == 'matching_out':
            count = self.env['cds.request_matching'].search_count([
                ('request_id', '=', self.id),
                ('partner_id', '=', partner_id.id),
                ('state', '=', 'matching'),
                ('user_id', '=', False),
            ])
            if count>0: 
                self.is_action_state = True
            else:
                self.is_action_state = False
        
        

    def action_start(self):
        """При начажтии Начать согласование, сбрасываем в таблице Согласующие данные по согласованию"""
        self.state = 'matching_in'
        for line in self.matching_ids:
            if line.is_local == True:
                line.state = 'matching'
            else:
                line.state = 'await'
            line.user_id = False
            line.date_state = False
            line.is_send = False


    def action_user_agreed(self):
        user = self.env.user
        partner_id = user.partner_id

        for line in self.matching_ids:
            if line.partner_id == partner_id:
                line.sudo().user_id = user.id
                line.sudo().state = 'agreed'
                line.sudo().date_state = datetime.now()






class CdsRequestMatching(models.Model):
    """Согласующие в Заявке Диспетчерской службы"""

    _name = "cds.request_matching"
    _description = "Согласующие"

    name = fields.Char("Наименование", compute="_get_name", store=True)
    partner_id = fields.Many2one('res.partner', string='Согласующий', domain="[('is_company', '=', False)]")
    function = fields.Char('Должность', related='partner_id.function')
    is_local = fields.Boolean(string='Внутренний согласующий', compute="_get_name", store=True)
    state = fields.Selection(selection=[
            ('await', 'Ожидание'), 
            ('matching', 'На согласовании'), 
            ('agreed', 'Согласовано'), 
            ('failure', 'Не согласовано'), 
        ], string="Статус", default='await', required=True, copy=False
    )
    user_id = fields.Many2one('res.users', string='Согласовал', readonly=False, copy=False)
    date_state = fields.Datetime(string='Дата отметки', readonly=True, copy=False)
    is_send = fields.Boolean(string='Отправлена?', readonly=True, copy=False)


    request_id = fields.Many2one('cds.request', ondelete='cascade', string=u"Заявка", required=True)

    @api.depends("partner_id")
    def _get_name(self):
        for record in self:
            if record.partner_id.parent_id:
                if record.partner_id.parent_id.is_company:
                    if record.partner_id.parent_id.id == record.env.company.id:
                        record.is_local = True
                        record.name = record.partner_id.name + ", " + record.partner_id.function
                    else:
                        record.is_local = False
                        record.name = record.partner_id.name
