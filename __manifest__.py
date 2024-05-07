# -*- coding: utf-8 -*-
{
    'name': "climbing_gym_website",

    'summary': """
       Website panels for Climbing gym""",

    'description': """
        Website panels for Climbing gym
    """,

    'author': "Miguel Hatrick",
    'website': "http://www.dacosys.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Administration',
    'version': '0.6.3b',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'board',
                'mail',
                'contacts',
                'website',
                'website_event',
                'website_form',
                'website_event_snippet_calendar',
                'event_registration_partner_unique',
                'portal',
                'partner_firstname',
                'climbing_gym'],
    # always loaded
    'data': [

        'views/portal/portal_layout_sidebar.xml',

        'views/portal/portal_my_documents.xml',
        'views/portal/portal_medical_certificate.xml',
        'views/portal/portal_member_access_package.xml',
        'views/portal/portal_member_membership.xml',
        'views/portal/portal_member_membership_request.xml',
        'views/portal/portal_monthly_event_group.xml',
        'views/portal/portal_reservation.xml',
        'views/portal/event_website_sale_templates.xml',
        'views/portal/portal_user_menu.xml',
        'views/portal/website_event_templates.xml',
        'views/portal/website_sale_templates.xml',

        'views/portal/portal_templates_extend.xml',

        'data/medical_certificate_form.xml',
        'data/member_membership_request_form.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
