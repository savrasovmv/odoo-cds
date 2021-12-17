from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    # 1С
    signature_image = fields.Image(string='Подпись (Img)', max_width=128, max_height=128,)

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights.
            Access rights are disabled by default, but allowed
            on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        cds_writable_fields = [
            'signature_image',
        ]

        

        init_res = super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = type(self).SELF_WRITEABLE_FIELDS + cds_writable_fields
        return init_res