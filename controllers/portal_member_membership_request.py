# -*- coding: utf-8 -*-
import datetime
import json
import pdb

from datetime import date
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo import fields, http, _
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class PortalMedicalCertificate(CustomerPortal):

    @http.route(['/my/member_membership_requests', '/my/member_membership_requests/page/<int:page>'], type='http',
                auth="user",
                website=True)
    def portal_my_member_membership_requests(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        _membershipRequest = request.env['climbing_gym.member_membership_request']

        domain = [
            ('partner_id', 'in', [partner.id]),
        ]

        searchbar_sortings = {
            'date': {'label': _('Creation date'), 'order': 'create_date desc'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        archive_groups = self._get_archive_groups('climbing_gym.member_membership_request', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = _membershipRequest.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/member_membership_requests",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,

            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        member_membership_requests = _membershipRequest.search(domain, order=sort_order, limit=self._items_per_page,
                                                               offset=pager['offset'])

        request.session['my_member_membership_requests_history'] = member_membership_requests.ids[:100]

        values.update({
            'date': date_begin,
            'member_membership_requests': member_membership_requests.sudo(),
            'page_name': 'member_membership_requests',

            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/member_membership_requests',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("climbing_gym_website.portal_my_member_membership_requests", values)

    @http.route(['/my/member_membership_requests/create'], type='http', auth="user", website=True)
    def portal_my_member_membership_request_form(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        _membershipRequest = request.env['climbing_gym.member_membership_request']

        domain = [
            ('partner_id', 'in', [partner.id]),
        ]

        values.update({
            'page_name': 'member_membership_requests',
            'page_operation': 'add',
            'default_url': '/my/member_membership_requests/create',
        })

        return request.render("climbing_gym_website.portal_my_member_membership_request_form", values)

    @http.route(['/my/member_membership_requests/<int:mc_id>'], type='http', auth="public", website=True)
    def portal_member_membership_request_page(self, mc_id, report_type=None, access_token=None, message=False,
                                              download=False, **kw):
        try:
            mc_sudo = self._document_check_access('climbing_gym.member_membership_request', mc_id,
                                                  access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # TODO: remove this
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=mc_sudo, report_type=report_type,
                                     report_ref='sale.action_report_saleorder',
                                     download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if mc_sudo:
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_member_membership_request_%s' % mc_sudo.id)
            if isinstance(session_obj_date, date):
                session_obj_date = session_obj_date.isoformat()
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_member_membership_request_%s' % mc_sudo.id] = now
                body = _('Membership request viewed by customer')
                _message_post_helper(res_model='climbing_gym.member_membership_request', res_id=mc_sudo.id,
                                     message=body,
                                     token=mc_sudo.access_token, message_type='notification', subtype="mail.mt_note",
                                     partner_ids=mc_sudo.user_id.sudo().partner_id.ids)

        values = {
            'member_membership_request': mc_sudo,
            'message': message,
            'token': access_token,
            'page_name': 'member_membership_requests',
            'return_url': '/my/member_membership_requests',
            'bootstrap_formatting': True,
            'partner_id': mc_sudo.partner_id.id,
            'report_type': 'html',
        }
        return request.render('climbing_gym_website.member_membership_request_portal_template', values)


class CustomerPortalForm(WebsiteForm):
    @http.route('/website_form/shop.climbing_gym.member_membership_request', type='http', auth="public",
                methods=['POST'],
                website=True)
    def website_form_member_membership_request(self, **kwargs):
        partner = request.env.user.partner_id
        model_record = request.env.ref('climbing_gym.model_climbing_gym_member_membership_request')

        # date
        date_of_birth = datetime.datetime.strptime(kwargs['date_of_birth'], "%Y-%m-%d").date()
        kwargs['date_of_birth'] = date_of_birth.strftime("%d/%m/%Y")

        try:
            data = self.extract_data(model_record, kwargs)
        except ValidationError as e:
            return json.dumps({'error_fields': e.args[0]})

        # TODO: what do i want to do here? shouldn't this be None?
        membership_id = request.env.ref('climbing_gym.model_climbing_gym_membership').search([('id', '=', 1)])

        _membershipRequest = request.env['climbing_gym.member_membership_request']

        _mc = _membershipRequest.sudo().create({
            'partner_id': partner.id,
            'date_of_birth': date_of_birth,
            'obs': kwargs['obs'],
            'membership_id': membership_id[0].id
        }
        )

        _mc.message_subscribe(partner_ids=[partner.id])

        # TODO: Add ticket or email here . It's better to use chatter
        if data['custom']:
            values = {
                'body': nl2br(data['custom']),
                'model': 'climbing_gym.member_membership_request',
                'message_type': 'comment',
                'no_auto_thread': False,
                'res_id': _mc.id,
            }
            request.env['mail.message'].sudo().create(values)

        if data['attachments']:
            _id = self.insert_attachment(model_record, _mc.id, data['attachments'])

        _at_ids = request.env['ir.attachment'].sudo().search(
            [('res_model', '=', 'climbing_gym.member_membership_request'),
             ('res_id', '=', _mc.id)])

        for _id in _at_ids:
            _mc.attachment_ids = [(4, _id.id)]

        return json.dumps({'id': _mc.id})
