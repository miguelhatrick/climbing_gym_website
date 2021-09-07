# -*- coding: utf-8 -*-
import pdb

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools import image_resize_images, image_resize_image, base64


class WebMedicalCertificate(models.Model):
    """Medical certificates of each climbing gym member Web addition"""
    _inherit = "climbing_gym.medical_certificate"

    def get_web_url(self):
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/my/medical_certificates/%s' % self.id
        return base_url
