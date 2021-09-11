# -*- coding: utf-8 -*-
import pdb

import babel.dates
import re
import werkzeug
import json

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import fields, http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import content_disposition, request

from odoo.http import request, route
from odoo.addons.sale.controllers.product_configurator import ProductConfiguratorController


class RequireMembership(ProductConfiguratorController):

    @http.route(['/product_configurator/get_combination_info'], type='json', auth="user", methods=['POST'])
    def get_combination_info(self, product_template_id, product_id, combination, add_qty, pricelist_id, **kw):
        """
        This function is used to block users from adding a product to a non member
        """
        res = super(
            RequireMembership, self).get_combination_info(product_template_id, product_id, combination, add_qty,
                                                          pricelist_id, **kw)
        _partner_id = request.env.user.partner_id
        _product_id = request.env['product.product'].search([('id', '=', res['product_id'])])

        _block = False

        if _product_id.climbing_gym_only_members:
            # only members
            if _partner_id is None or _partner_id.climbing_gym_main_member_membership_id is None or len(
                    _partner_id.climbing_gym_main_member_membership_id) == 0:
                _block = True

            if _product_id.climbing_gym_only_active_members and _partner_id.climbing_gym_main_member_membership_id.state not in ['active'] :
                _block = True

        if _block:
            res.update({
                'is_combination_possible': False,
            })
        return res
