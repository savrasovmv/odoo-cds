# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class Settings(models.TransientModel):
    """Настройки параметров Заявок"""
    _inherit = 'res.config.settings'

    # Настройки параметров Заявок
    request_is_notify_time_off = fields.Boolean(u'Напоминать об окончании заявки?', default=True)
    request_hour_notify_time_off = fields.Integer('За сколько часов отправлять напоминание об окончании заявки', default=2)
    request_dispetcher_user_id = fields.Many2one('res.users', string='Диспетчер')
    
    request_manager_user_id = fields.Many2one('res.users', string='Руководитель ЦДС')

    
    @api.model
    def get_values(self):
        res = super(Settings, self).get_values()
        conf = self.env['ir.config_parameter']
        res.update({
                'request_is_notify_time_off': conf.get_param('request_is_notify_time_off'),
                'request_hour_notify_time_off': int(conf.get_param('request_hour_notify_time_off')),
                'request_dispetcher_user_id': int(conf.get_param('request_dispetcher_user_id')),
                'request_manager_user_id': int(conf.get_param('request_manager_user_id')),
                
        })
        return res


    def set_values(self):
        super(Settings, self).set_values()
        conf = self.env['ir.config_parameter']
        conf.set_param('request_is_notify_time_off', self.request_is_notify_time_off)
        conf.set_param('request_hour_notify_time_off', int(self.request_hour_notify_time_off))
        conf.set_param('request_dispetcher_user_id', int(self.request_dispetcher_user_id.id)  or False)
        conf.set_param('request_manager_user_id', int(self.request_manager_user_id.id)  or False)