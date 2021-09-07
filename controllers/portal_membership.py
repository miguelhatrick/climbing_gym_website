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

    # TODO: ADD MEMBERSHIP STATUS
    @http.route(['/my/membermemberships', '/my/membermemberships/page/<int:page>'], type='http', auth="user",
                website=True)
    def portal_my_member_memberships(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        _memberMembership = request.env['climbing_gym.member_membership']

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

        archive_groups = self._get_archive_groups('climbing_gym.member_membership', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = _memberMembership.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/membermemberships",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        member_memberships = _memberMembership.search(domain, order=sort_order, limit=self._items_per_page,
                                                      offset=pager['offset'])

        request.session['my_membermemberships_history'] = member_memberships.ids[:100]

        values.update({
            'date': date_begin,
            'member_memberships': member_memberships.sudo(),
            'page_name': 'Member membership',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/membermemberships',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("climbing_gym_website.portal_my_member_memberships", values)
