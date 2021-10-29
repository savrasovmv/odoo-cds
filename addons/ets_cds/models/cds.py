from odoo import fields, models, api
from odoo import tools
from odoo.tools import html2plaintext
import base64


class CdsDepartment(models.Model):
    """Справочник Подразделения"""

    _name = "cds.department"
    _description = "Подразделения"

    name = fields.Char("Наименование", required=True)


class CdsLocation(models.Model):
    """Справочник Местонахождение"""

    _name = "cds.location"
    _description = "Местонахождение"

    name = fields.Char("Наименование", required=True)


class CdsObjectType(models.Model):
    """Справочник Типы объектов"""

    _name = "cds.object_type"
    _description = "Типы объектов"

    name = fields.Char("Наименование", required=True)



class CdsObjectClass(models.Model):
    """Справочник Класс объектов"""

    _name = "cds.object_class"
    _description = "Класс объектов"

    name = fields.Char("Наименование", required=True)



class CdsEnergyComplex(models.Model):
    """"Справочник Энергокомплекс"""

    _name = "cds.energy_complex"
    _description = "Энергокомплекс"

    name = fields.Char("Наименование", required=True)
    company_partner_id = fields.Many2one('res.partner', string='Заказчик', domain="[('is_company', '=', True)]")
    location_id = fields.Many2one('cds.location', string='Местонахождение')
    description = fields.Html("Описание", help="Описание энергокомплекса")

    matching_ids = fields.One2many('cds.energy_complex_matching', 'energy_complex_id', string=u"Строка Согласующие")




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
        if self.partner_id.parent_id:
            if self.partner_id.parent_id.is_company:
                if self.partner_id.parent_id.id == self.env.company.id:
                    self.is_local = True
                    self.name = self.partner_id.name + ", " + self.partner_id.function
                else:
                    self.is_local = False
                    self.name = self.partner_id.name
    


class CdsEnergyComplexObject(models.Model):
    """"Объекты в Энергокомплексе"""

    _name = "cds.energy_complex_object"
    _description = "Объекты"

    name = fields.Char("Наименование", compute="_get_name", store=True)
    name_partner = fields.Char("Наименование для заказчика", required=True)
    object_type_id = fields.Many2one('cds.object_type', string='Тип', required=True)
    object_class_id = fields.Many2one('cds.object_class', string='Класс', required=True)
    serial = fields.Char(string='Номер', required=True)

    energy_complex_id = fields.Many2one('cds.energy_complex', ondelete='cascade', string=u"Энергокомплекс", required=True)



