# -*- coding: utf-8 -*-
import pdb
from datetime import date
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    HEALTH_FIELDS = [
        "health_insurance" ,
        "health_insurance_number" ,
        "health_insurance_emergency_phone",
        "emergency_contact_name" ,
        "emergency_contact_relationship",
        "emergency_contact_phone",
    ]
    def __init__(self):
        self.OPTIONAL_BILLING_FIELDS = super(CustomerPortal, self).OPTIONAL_BILLING_FIELDS
        self.OPTIONAL_BILLING_FIELDS.extend(self.HEALTH_FIELDS)

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        _partner = request.env.user.partner_id

        event_registration = request.env['event.registration']
        event_registration_count = event_registration.search_count([
            ('partner_id', 'in', [_partner.id]),
            # ('state', 'in', ['sent', 'cancel'])
        ])

        # pdb.set_trace()

        member_access_package = request.env['climbing_gym.member_access_package']
        member_access_package_count = member_access_package.search_count([
            ('partner_id', 'in', [_partner.id]),
            # ('state', 'in', ['sale', 'done'])
        ])

        medical_certificate = request.env['climbing_gym.medical_certificate']
        medical_certificate_count = medical_certificate.search_count([
            ('partner_id', 'in', [_partner.id]),
            # ('state', 'in', ['sale', 'done'])
        ])

        member_membership = request.env['climbing_gym.member_membership']
        member_membership_count = member_membership.search_count([
            ('partner_id', 'in', [_partner.id]),
            # ('state', 'in', ['sale', 'done'])
        ])

        # TODO: REMOVE THIS FROM HERE
        # member_membership_request = request.env['climbing_gym.member_membership_request']
        # member_membership_request_count = member_membership_request.search_count([
        #     ('partner_id', 'in', [_partner.id]),
        #     # ('state', 'in', ['sale', 'done'])
        # ])

        _monthly_event_group = request.env['climbing_gym.event_monthly_group']
        _monthly_event_group_count = _monthly_event_group.search_count([
            ('state', 'in', ['active']),
            # ('state', 'in', ['sale', 'done'])
        ])

        values.update({
            'event_registration_count': event_registration_count,
            'member_access_package_count': member_access_package_count,
            'medical_certificate_count': medical_certificate_count,
            'member_membership_count': member_membership_count,
            # 'member_membership_request_count': member_membership_request_count,
            'monthly_event_groups_count': _monthly_event_group_count,
        })
        return values
