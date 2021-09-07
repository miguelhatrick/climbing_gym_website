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

    @http.route(['/my/memberaccesspackages', '/my/memberaccesspackages/page/<int:page>'], type='http', auth="user",
                website=True)
    def portal_my_memberaccesspackages(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
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
            url="/my/memberaccesspackages",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        member_access_packages = MemberAccessPackages.search(domain, order=sort_order, limit=self._items_per_page,
                                                             offset=pager['offset'])
        request.session['my_memberaccesspackages_history'] = member_access_packages.ids[:100]

        values.update({
            'date': date_begin,
            'member_access_packages': member_access_packages.sudo(),
            'page_name': 'Member access packages',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/memberaccesspackages',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("climbing_gym_website.portal_my_member_access_packages", values)
