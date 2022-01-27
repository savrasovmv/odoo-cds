from odoo import fields, models, api
from odoo import tools
from odoo.tools import html2plaintext
import base64


class CdsDepartment(models.Model):
    """Справочник Подразделения"""

    _name = "cds.department"
    _description = "Подразделения"

    name = fields.Char("Наименование", required=True)
    active = fields.Boolean(default=True)



class CdsLocation(models.Model):
    """Справочник Местонахождение"""

    _name = "cds.location"
    _description = "Местонахождение"

    name = fields.Char("Наименование", required=True)
    active = fields.Boolean(default=True)



class CdsObjectType(models.Model):
    """Справочник Типы объектов"""

    _name = "cds.object_type"
    _description = "Типы объектов"

    name = fields.Char("Наименование", required=True)
    active = fields.Boolean(default=True)




class CdsObjectClass(models.Model):
    """Справочник Класс объектов"""

    _name = "cds.object_class"
    _description = "Класс объектов"

    name = fields.Char("Наименование", required=True)
    active = fields.Boolean(default=True)




class CdsEnergyComplex(models.Model):
    """"Справочник Энергокомплекс"""

    _name = "cds.energy_complex"
    _description = "Энергокомплекс"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    name = fields.Char("Наименование", required=True)
    active = fields.Boolean(default=True)

    company_partner_id = fields.Many2one('res.partner', string='Заказчик', domain="[('is_company', '=', True)]")
    location_id = fields.Many2one('cds.location', string='Местонахождение')
    description = fields.Html("Описание", help="Описание энергокомплекса")
    object_count = fields.Integer(string='Количество объектов', compute='_get_object_count')
    request_count = fields.Integer(string='Количество заявок', compute='_get_request_count')
    attachment_ids = fields.One2many('ir.attachment', compute='_compute_attachment_ids', string="Main Attachments",
        help="Attachment that don't come from message.")
    # attachment_ids = fields.Many2many('ir.attachment', string='Вложения')
    # attachment_ids = fields.Many2many('ir.attachment', 'cds_energy_complex_ir_attachments_rel',
    #     'energy_complex_id', 'attachment_id', string='Вложения')

    user_id = fields.Many2one('res.users', string='Ответственный')

    matching_ids = fields.One2many('cds.energy_complex_matching', 'energy_complex_id', string=u"Строки Согласующие")
    request_ids = fields.One2many('cds.request', 'energy_complex_id', string=u"Строки Заявки")
    object_ids = fields.One2many('cds.energy_complex_object', 'energy_complex_id', string=u"Строки Заявки")


    def _compute_attachment_ids(self):
        for record in self:
            attachment_ids = self.env['ir.attachment'].search([('res_id', '=', record.id), ('res_model', '=', 'cds.energy_complex')]).ids
            print("++++++++attachment_ids", attachment_ids)
            message_attachment_ids = record.mapped('message_ids.attachment_ids').ids  # from mail_thread
            record.attachment_ids = [(6, 0, list(set(attachment_ids) - set(message_attachment_ids)))]

    @api.depends('matching_ids')
    def _get_object_count(self):
        for record in self:
            record.object_count = len(record.object_ids)

    @api.depends('request_ids')
    def _get_request_count(self):
        for record in self:
            record.request_count = len(record.request_ids)

    def _compute_attachment_ids(self):
        for record in self:
            attachment_ids = self.env['ir.attachment'].search([('res_id', '=', record.id), ('res_model', '=', 'cds.energy_complex')]).ids
            # message_attachment_ids = task.mapped('message_ids.attachment_ids').ids  # from mail_thread
            record.attachment_ids = [(6, 0, list(set(attachment_ids)))]

    def action_request(self):
        action = self.env['ir.actions.act_window']._for_xml_id('ets_cds.cds_request_action')
        ctx = dict(self.env.context)
        ctx.update({'search_default_energy_complex_id': self.ids[0],
                    })
        action['context'] = ctx
        return action
    
    def action_cds_object(self):
        action = self.env['ir.actions.act_window']._for_xml_id('ets_cds.cds_energy_complex_object_action')
        ctx = dict(self.env.context)
        ctx.update({'search_default_energy_complex_id': self.ids[0],
                    })
        action['context'] = ctx
        return action

    




class CdsEnergyComplexMatching(models.Model):
    """"Шаблоны согласующих в Энергокомплексе"""

    _name = "cds.energy_complex_matching"
    _description = "Согласующие"

    name = fields.Char("Наименование", compute="_get_name", store=True)
    partner_id = fields.Many2one('res.partner', string='Согласующие', domain="[('is_company', '=', False)]")
    function = fields.Char('Должность', related='partner_id.function')

    is_local = fields.Boolean(string='Внутренний согласующий', compute="_get_name", store=True)

    energy_complex_id = fields.Many2one('cds.energy_complex', ondelete='cascade', string=u"Энергокомплекс", required=True)

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
    


class CdsEnergyComplexObject(models.Model):
    """"Объекты в Энергокомплексе"""

    _name = "cds.energy_complex_object"
    _description = "Объекты"

    name = fields.Char("Наименование", compute="_get_name", store=True)
    active = fields.Boolean(default=True)

    is_name_partner = fields.Boolean(string='Другое имя для заказчика')
    name_partner = fields.Char("Наименование для заказчика")
    object_type_id = fields.Many2one('cds.object_type', string='Тип', required=True)
    object_class_id = fields.Many2one('cds.object_class', string='Класс', required=True)
    serial = fields.Char(string='Номер', required=True)
    description = fields.Html("Описание", help="Описание энергокомплекса")
    attachment_ids = fields.Many2many('ir.attachment', string='Вложения')


    energy_complex_id = fields.Many2one('cds.energy_complex', ondelete='cascade', string=u"Энергокомплекс", required=True)


    @api.depends("object_type_id", "object_class_id", "serial")
    def _get_name(self):
        
        name = ""

        if self.object_type_id:
            name += self.object_type_id.name

        if self.serial:
            name += '-' + self.serial

        if self.object_class_id:
            name += ' ' + self.object_class_id.name

        if len(name)>0:
            self.name = name




