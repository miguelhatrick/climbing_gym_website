# -*- coding: utf-8 -*-
import pdb

from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools import image_resize_images, image_resize_image, base64


class WebMedicalCertificate(models.Model):
    """Medical certificates of each climbing gym member Web addition"""
    _inherit = ['climbing_gym.medical_certificate', 'portal.mixin']
    _name = 'climbing_gym.medical_certificate'

    def get_web_url(self):
        base_url = request.env['ir.config_parameter'].get_param('web.base.url')
        base_url += '/my/medical_certificates/%s' % self.id
        return base_url

    def _compute_access_url(self):
        super(WebMedicalCertificate, self)._compute_access_url()
        for myobject in self:
            myobject.access_url = '/my/medical_certificates/%s' % myobject.id

    @api.multi
    def _get_share_url(self, redirect=False, signup_partner=False, pid=None):
        """Override for sales order.

        If the SO is in a state where an action is required from the partner,
        return the URL with a login token. Otherwise, return the URL with a
        generic access token (no login).
        """
        self.ensure_one()
        # if self.state not in ['sale', 'done']:
        auth_param = url_encode(self.partner_id.signup_get_auth_param()[self.partner_id.id])
        return self.get_portal_url(query_string='&%s' % auth_param)
        # return super(WebMedicalCertificate, self)._get_share_url(redirect, signup_partner, pid)

    @api.multi
    def preview_medical_certificate(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }
