# -*- coding: utf-8 -*-
import pdb
from datetime import date
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class CustomerPortalClimbingGym(CustomerPortal):

    OPTIONAL_HEALTH_FIELDS = [
        "birthdate_date" ,
        "health_insurance" ,
        "health_insurance_number" ,
        "health_insurance_emergency_phone",
        "emergency_contact_name" ,
        "emergency_contact_relationship",
        "emergency_contact_phone",
    ]

    def __init__(self):
        values = super(CustomerPortal, self).__init__()
        self.OPTIONAL_BILLING_FIELDS = self.OPTIONAL_BILLING_FIELDS + self.OPTIONAL_HEALTH_FIELDS
