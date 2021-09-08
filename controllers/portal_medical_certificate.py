# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import json
import pdb

from datetime import date
from odoo.addons.website_form.controllers.main import WebsiteForm
from addons_custom.climbing_gym.models.medical_certificate import MedicalCertificate
from odoo import fields, http, _
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class PortalMedicalCertificate(CustomerPortal):

    @http.route(['/my/medical_certificates', '/my/medical_certificates/page/<int:page>'], type='http', auth="user",
                website=True)
    def portal_my_medical_certificates(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        _medicalCertificate = request.env['climbing_gym.medical_certificate']

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

        archive_groups = self._get_archive_groups('climbing_gym.medical_certificate', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = _medicalCertificate.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/medical_certificates",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,

            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        medical_certificates = _medicalCertificate.search(domain, order=sort_order, limit=self._items_per_page,
                                                          offset=pager['offset'])

        request.session['my_medical_certificates_history'] = medical_certificates.ids[:100]

        values.update({
            'date': date_begin,
            'medical_certificates': medical_certificates.sudo(),
            'page_name': 'medical_certificates',

            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/medical_certificates',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("climbing_gym_website.portal_my_medical_certificates", values)

    @http.route(['/my/medical_certificates/create'], type='http', auth="user", website=True)
    def portal_my_medical_certificate_form(self, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        _medicalCertificate = request.env['climbing_gym.medical_certificate']

        domain = [
            ('partner_id', 'in', [partner.id]),
        ]

        values.update({
            'page_name': 'medical_certificates',
            'page_operation': 'add',

            'default_url': '/my/medical_certificates/create',
        })

        return request.render("climbing_gym_website.portal_my_medical_certificate_form", values)

    @http.route(['/my/medical_certificates/<int:mc_id>'], type='http', auth="public", website=True)
    def portal_medical_certificate_page(self, mc_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            mc_sudo = self._document_check_access('climbing_gym.medical_certificate', mc_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=mc_sudo, report_type=report_type,
                                     report_ref='sale.action_report_saleorder',
                                     download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if mc_sudo:
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_medical_certificate_%s' % mc_sudo.id)
            if isinstance(session_obj_date, date):
                session_obj_date = session_obj_date.isoformat()
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_medical_certificate_%s' % mc_sudo.id] = now
                body = _('Medical certificate viewed by customer')
                _message_post_helper(res_model='climbing_gym.medical_certificate', res_id=mc_sudo.id, message=body,
                                     token=mc_sudo.access_token, message_type='notification', subtype="mail.mt_note",
                                     partner_ids=mc_sudo.user_id.sudo().partner_id.ids)

        values = {
            'medical_certificate': mc_sudo,
            'message': message,
            'token': access_token,
            'page_name': 'medical_certificates',
            'return_url': '/my/medical_certificates',
            'bootstrap_formatting': True,
            'partner_id': mc_sudo.partner_id.id,
            'report_type': 'html',
        }
        return request.render('climbing_gym_website.medical_certificate_portal_template', values)



class CustomerPortalForm(WebsiteForm):
    @http.route('/website_form/shop.climbing_gym.medical_certificate', type='http', auth="public", methods=['POST'],
                website=True)
    def website_form_medical_certificate(self, **kwargs):
        partner = request.env.user.partner_id
        model_record = request.env.ref('climbing_gym.model_climbing_gym_medical_certificate')

        # date
        issue_date = datetime.datetime.strptime(kwargs['issue_date'], "%Y-%m-%d").date()
        kwargs['issue_date'] = issue_date.strftime("%d/%m/%Y")

        try:
            data = self.extract_data(model_record, kwargs)
        except ValidationError as e:
            return json.dumps({'error_fields': e.args[0]})

        _medicalCertificate: MedicalCertificate = request.env['climbing_gym.medical_certificate']

        _mc = _medicalCertificate.sudo().create({
            'partner_id': partner.id,
            'issue_date': issue_date,
            'doctor_name': kwargs['doctor_name'],
            'doctor_license': kwargs['doctor_license']
        }
        )

        _mc.message_subscribe(partner_ids=[partner.id])

        # TODO: Add ticket or email here . It's better to use chatter
        if data['custom']:
            values = {
                'body': nl2br(data['custom']),
                'model': 'climbing_gym.medical_certificate',
                'message_type': 'comment',
                'no_auto_thread': False,
                'res_id': _mc.id,
            }
            request.env['mail.message'].sudo().create(values)

        if data['attachments']:
            _id = self.insert_attachment(model_record, _mc.id, data['attachments'])

        _at_ids = request.env['ir.attachment'].sudo().search([('res_model', '=', 'climbing_gym.medical_certificate'),
                                                              ('res_id', '=', _mc.id)])

        for _id in _at_ids:
            _mc.attachment_ids = [(4, _id.id)]

        return json.dumps({'id': _mc.id})


