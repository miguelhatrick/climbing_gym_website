# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pdb
from datetime import date
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class CustomerPortal(CustomerPortal):

    @http.route(['/my/member_access_packages', '/my/member_access_packages/page/<int:page>'], type='http', auth="user",
                website=True)
    def portal_my_member_access_packages(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        MemberAccessPackages = request.env['climbing_gym.member_access_package']

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

        archive_groups = self._get_archive_groups('climbing_gym.member_access_package', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = MemberAccessPackages.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/member_access_packages",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        member_access_packages = MemberAccessPackages.search(domain, order=sort_order, limit=self._items_per_page,
                                                             offset=pager['offset'])
        request.session['my_member_access_packages_history'] = member_access_packages.ids[:100]

        values.update({
            'date': date_begin,
            'member_access_packages': member_access_packages.sudo(),
            'page_name': 'member_access_packages',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/member_access_packages',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("climbing_gym_website.portal_my_member_access_packages", values)

    @http.route(['/my/member_access_packages/<int:mc_id>'], type='http', auth="public", website=True)
    def portal_member_access_package_page(self, mc_id, report_type=None, access_token=None, message=False,
                                          download=False, **kw):
        try:
            mm_sudo = self._document_check_access('climbing_gym.member_access_package', mc_id,
                                                  access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # if report_type in ('html', 'pdf', 'text'):
        #    return self._show_report(model=mc_sudo, report_type=report_type,
        #                             report_ref='sale.action_report_saleorder',
        #                             download=download)

        # use sudo to allow accessing/viewing orders for public user
        # only if he knows the private token
        # Log only once a day
        if mm_sudo:
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_member_access_package_%s' % mm_sudo.id)

            if isinstance(session_obj_date, date):
                session_obj_date = session_obj_date.isoformat()
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_member_access_package_%s' % mm_sudo.id] = now
                body = _('Member access package viewed by customer')
                _message_post_helper(res_model='climbing_gym.member_access_package', res_id=mm_sudo.id, message=body,
                                     token=mm_sudo.access_token, message_type='notification', subtype="mail.mt_note",
                                     partner_ids=request.env.user.partner_id)

        values = {
            'member_access_package': mm_sudo,
            'message': message,
            'token': access_token,
            'page_name': 'member_access_packages',
            'return_url': '/my/member_access_packages',
            'bootstrap_formatting': True,
            'partner_id': mm_sudo.partner_id.id,
            'report_type': 'html',
        }
        return request.render('climbing_gym_website.member_access_package_portal_template', values)
