# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo.addons.mail.controllers.main import MailController
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class CrmController(http.Controller):

    @http.route('/request/draft', type='http', auth='user', methods=['GET'])
    def crm_lead_case_mark_won(self, res_id, token):
        comparison, record, redirect = MailController._check_token_and_record_or_redirect('cds.request', int(res_id), token)
        if comparison and record:
            try:
                record.sudo().action_cancel()
            except Exception:
                _logger.exception("Не удалось отменить заявку")
                return MailController._redirect_to_messaging()
        return redirect
    
