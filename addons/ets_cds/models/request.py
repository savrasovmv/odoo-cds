from odoo import fields, models, api, _
from odoo import tools
from odoo.tools import html2plaintext
import base64
from datetime import datetime



class CdsRequest(models.Model):
    """Заявки Диспетчерской службы"""

    _name = "cds.request"
    _description = "Заявки"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char('Номер', copy=False, readonly=True, default=lambda x: _('New'))
    date = fields.Datetime(string='Дата', copy=False, readonly=True, default=fields.Datetime.now)

    user_id = fields.Many2one('res.users', copy=False, string='Пользователь', readonly=True, default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', copy=False, string='Сотрудник', related='user_id.partner_id', store=True)
    function = fields.Char('Должность', copy=False, related='partner_id.function', store=True)

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
        default=lambda self: self.env.company)
    

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

    is_extend = fields.Boolean('Продлена')
    date_extend = fields.Datetime('Дата продления')

    energy_complex_id = fields.Many2one('cds.energy_complex', string='Энергокомплекс')
    location_id = fields.Many2one('cds.location', string='Местонахождение', related='energy_complex_id.location_id', store=True)
    company_partner_id = fields.Many2one('res.partner', string='Заказчик', related='energy_complex_id.company_partner_id', store=True)
    object_id = fields.Many2one('cds.energy_complex_object', string='Объект')

    work_name = fields.Text('Наименование работ')
    
    description_mode = fields.Text("Режимные указания")

    total_load_gpes = fields.Char('Общая нагрузка ГПЭС')
    restrictions = fields.Char(string='Ограничения', default='нет')
    oil_losses = fields.Char(string='Потери нефти', default='нет')

    date_hand_over = fields.Datetime(string='Дата передачи', copy=False, read=['ets_cds.group_cds_executor'])

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
        tracking=True
    )

    date_turn_off = fields.Datetime(string='Отключение', copy=False)
    date_turn_on = fields.Datetime(string='Включение', copy=False)

    description_partner = fields.Text("Комментарий для заказчика")
    description = fields.Text("Комментарии к заявке")

    attachment_ids = fields.Many2many('ir.attachment', 'cds_request_ir_attachments_rel',
        'request_id', 'attachment_id', string='Вложения')


    matching_ids = fields.One2many('cds.request_matching', 'request_id', string=u"Строки Согласующие")

    is_action_state = fields.Boolean(string='Действия для пользователя', compute="_get_action_state_user", help="Признак тредуется ли действие от пользователя на текущем статусе заявки, True - действие требуется, False - действий не требуется")

    action_state = fields.Char(string='Состояние', compute="_get_action_state", help="Текстовое описание состояния в текущем статусе")
    is_end_state = fields.Boolean(string='Этап выполнен?', compute="_get_action_state", help="Если истина, то этап завершен и требуется дальнейшее действие")
    is_time_up = fields.Boolean(string='Время истекло?', compute="_get_time_up", help="Если истина, то текущее время больше чем Дата окончания работ")

    
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

    def _track_subtype(self, init_values):
        # init_values contains the modified fields' values before the changes
        #
        # the applied values can be accessed on the record as they are already
        # in cache
        self.ensure_one()
        if 'state' in init_values and self.state == 'matching_in':
            return self.env.ref('ets_cds.mt_state_change')
        return super(CdsRequest, self)._track_subtype(init_values)


    def _get_time_up(self):
        for record in self:
            record.is_time_up = False
            if record.date_work_end:
                if (record.date_work_end < datetime.now() and record.state=="open" and record.date_turn_on == False) or (record.date_turn_on != False and record.date_work_end<record.date_turn_on):
                    record.is_time_up = True
                


    @api.depends('matching_ids')
    def _get_action_state(self):
        """Отображает информацию в заголовке заявки, по текущему состоянию и необходимых действиях"""

        self.ensure_one()
        self.action_state = self.state
        self.is_end_state = False

        if self.state == 'draft':
            self.action_state = "Черновик. Нажмите Начать, что бы зпустить процесс согласования"
        if self.state == 'matching_in':
            matching = self.env['cds.request_matching'].search([
                ('request_id', '=', self.id),
                ('is_local', '=', True),
                ('state', '=', 'matching'),
                ('user_id', '=', False),
            ])
            count = len(matching)
            if count>0: 
                self.action_state = "Ожидает согласования от %s пользователей: %s" % (count, matching.mapped('partner_id.name'))
            else:
                self.action_state = "Внутреннее согласование завершено. Необходимо перейти к следующему этапу"
                self.is_end_state = True
        
        if self.state == 'matching_out':
            count = self.env['cds.request_matching'].search_count([
                ('request_id', '=', self.id),
                ('is_local', '=', False),
                ('state', '=', 'matching'),
                ('user_id', '=', False),
            ])
            if count>0: 
                self.action_state = "Ожидает согласования от %s заказчика" % (count)
            else:
                self.action_state = "Согласование с заказчиком завершено. Необходимо перейти к следующему этапу"
                self.is_end_state = True

        if self.state == 'agreed':
            self.action_state = "Заявка согласована. Ожидания начала работ"
            self.is_end_state = True
        
        if self.state == 'open':
            if self.is_time_up:
                self.action_state = "Заявка открыта. Время истекло. Продлите время выполнения заявку"
                self.is_end_state = True
            else:
                self.action_state = "Заявка открыта"
        
        if self.state == 'extend':
            self.action_state = "Заявка продлена"
        
        if self.state == 'close':
            self.action_state = "Заявка закрыта"
            self.is_end_state = True

        if self.state == 'failure':
            self.action_state = "Заявка Не согласована"
            self.is_end_state = True
        
        if self.state == 'cancel':
            self.action_state = "Заявка Отменена"
            self.is_end_state = True



    def _get_action_state_user(self):
        """Устанавливает признак необходимости действия для текущего пользователя"""

        self.ensure_one()
        self.is_action_state = False
        user = self.env.user
        partner_id = user.partner_id

        # Внутреннее согласование и текущий пользователь есть в списке согласующих
        if self.state == 'matching_in':
            count = self.env['cds.request_matching'].search_count([
                ('request_id', '=', self.id),
                ('partner_id', '=', partner_id.id),
                ('state', '=', 'matching'),
                ('is_local', '=', True),
                ('user_id', '=', False),
            ])
            if count>0: 
                self.is_action_state = True

        if self.state == 'matching_out':
            count = self.env['cds.request_matching'].search_count([
                ('request_id', '=', self.id),
                ('partner_id', '=', partner_id.id),
                ('state', '=', 'matching'),
                ('is_local', '=', False),
                ('user_id', '=', False),
            ])
            if count>0: 
                self.is_action_state = True
            
        
        
    def action_user_agreed(self):
        """Действие Согласованно в форме заявки"""

        user = self.env.user
        partner_id = user.partner_id

        for record in self:
            for line in record.matching_ids:
                if line.partner_id == partner_id:
                    # line.sudo().user_id = user.id
                    line.sudo().state = 'agreed'
                    # line.sudo().date_state = datetime.now()
    
    def action_user_failure(self):
        """Действие Отказать в согласование в форме заявки"""
        self.ensure_one()
        user = self.env.user
        partner_id = user.partner_id

        for line in self.matching_ids:
            if line.partner_id == partner_id:
                line.sudo().user_id = user.id
                line.sudo().state = 'failure'
                line.sudo().date_state = datetime.now()


    ############################################
    # Действия по изменению статуса Заявки
    ############################################

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
        # partner_ids=[line.partner_id.id for line in self.matching_ids]
        # self.message_post(body="Тестовая отправка", partner_ids=[9])
        # print("+++++++++++++++")

    # def _notify_get_groups(self, msg_vals=None):
    #     """ Handle Trip Manager recipients that can cancel the trip at the last
    #     minute and kill all the fun. """
    #     print("+++++++++++++++")
    #     print("+++++++++++++++message", msg_vals)
    #     groups = super(CdsRequest, self)._notify_get_groups(msg_vals=msg_vals)
    #     print("+++++++++++++++groups", groups)

    #     self.ensure_one()
    #     if self.state == 'matching_in':
    #         local_msg_vals = dict(msg_vals or {})
    #         app_action = self._notify_get_action_link('controller', controller='/request/draft', **local_msg_vals)
    #         # app_action = self._notify_get_action_link('method',
    #         #                     method='action_cancel')
    #         trip_actions = [{'url': app_action, 'title': _('Cancel')}]

    #     new_group = (
    #         'group_cds_matching',
    #         lambda pdata: pdata['type'] == 'user',
    #         {
    #             'actions': trip_actions,
    #         })
        
    #     print("+++++++++++++++new_group", new_group)
    #     return [new_group] + groups



    def action_send_out_matching(self):
        """ Действие Отправить на внешнее согласование в форме заявки. 
            Переводит в статус Внешнее согласование
            Устанавливает дату передачи на согласование"""
        
        self.state = 'matching_out'
        self.date_hand_over = datetime.now()
        for line in self.matching_ids:
            if line.is_local == False and line.state == 'await':
                line.state = 'matching'
                line.user_id = False
                line.date_state = False
                line.is_send = False

    def action_start_work(self):
        """ Действие Начало выполнения работ.
            Устанавливает в статус Открыта. Меняет дату Отключения"""
        
        for record in self:
            record.state = 'open'
            record.date_turn_off = datetime.now()
    
    def action_extend_work(self):
        """ Действие Продлить выполнения работ.
            Устанавливает в статус Продлена"""
        
        for record in self:
            record.state = 'extend'

    def action_end_work(self):
        """ Действие Работы выполнены.
            Устанавливает в статус Закрыта. Меняет дату Включения"""
        
        for record in self:
            record.state = 'close'
            record.date_turn_on = datetime.now()

    def action_cancel(self):
        """ Действие Отменить заявку.
            Устанавливает в статус Отменена"""
        
        for record in self:
            record.state = 'cancel'
        
        

        
    def action_send_mail_local_matching(self):
        """Отправляет письмо внутренним согласующим"""
        template = self.env.ref('ets_cds.mail_template_request_local_matching')
        
        for record in self:

            matching_list = self.env['cds.request_matching'].search([
                ('request_id', '=', record.id),
                ('is_local', '=', True),
                '|',
                ('state', '=', 'matching'),
                ('state', '=', 'await'),
            ])

            if len(matching_list)>0:
                # email_values={
                #    'fff': "sdfsdfsdf",
                # }
                # record.with_context(email_values).message_post_with_template(
                record.message_post_with_template(
                    template.id, composition_mode='comment',
                    model='cds.request', res_id=record.id,
                    partner_ids=[line.partner_id.id for line in self.matching_ids],
                    # email_layout_xmlid='mail.mail_notification_light',
                )
            # email_to = record.get_registration_email()
            
            # if email_to:
            #     email_values={
            #        'email_to': email_to,
            #     }
            #     template.send_mail(record.id, force_send=True, email_values=email_values)

            # else:
            #     return False

        






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
    user_id = fields.Many2one('res.users', string='Согласовал', copy=False, compute="_change_status", store=True)
    date_state = fields.Datetime(string='Дата отметки', copy=False, compute="_change_status", store=True)
    is_send = fields.Boolean(string='Отправлена?', readonly=True, copy=False)
    is_action_state = fields.Boolean(string='Действия для пользователя', compute="_get_action_state_user", help="Признак требуется ли действие от       пользователя на текущем статусе заявки, True - действие требуется, False - действий не требуется")
    matching_method = fields.Selection(selection=[
            ('self', 'Лично'), 
            ('tel', 'По телефону'), 
            ('email', 'По email'), 
        ], string="Метод согласования ", default='', copy=False
    )
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


    @api.depends("state")
    def _change_status(self):
        
        user = self.env.user
        for record in self:
            if record.state == 'await' or record.state == 'matching':
                record.user_id = False
                record.date_state = False
            if record.state == 'agreed' or record.state == 'failure':
                record.user_id = user.id
                record.date_state = datetime.now()


    def _get_action_state_user(self):
        """Устанавливает признак необходимости действия для текущего пользователя"""

        for line in self:
            line.is_action_state = False
            if line.state == 'matching':
                line.is_action_state = True
            else:
                line.is_action_state = False


    def action_user_agreed(self):
        """Действие Согласованно в форме строки согласующих заявки"""

        self.ensure_one()
        user = self.env.user
        self.sudo().user_id = user.id
        self.sudo().state = 'agreed'
        self.sudo().date_state = datetime.now()


    def action_user_failure(self):
        """Действие Отказать в форме строки согласующих заявки"""

        self.ensure_one()
        user = self.env.user
        self.sudo().user_id = user.id
        self.sudo().state = 'failure'
        self.sudo().date_state = datetime.now()

    
    def action_user_clear(self):
        """Действие Очистить поле"""

        self.ensure_one()
        user = self.env.user
        self.sudo().user_id = False
        self.sudo().date_state = False
        self.sudo().state = 'await'
        if self.request_id.state == 'matching_in' and self.is_local:
            self.sudo().state = 'matching'
        if self.request_id.state == 'matching_out' and not self.is_local:
            self.sudo().state = 'matching'
        
        self.request_id._get_action_state()
        self.request_id._get_action_state_user()