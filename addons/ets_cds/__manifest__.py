# -*- coding: utf-8 -*-
{
    'name': "Управление заявками ЦДС",

    'summary': """
        Модуль для Управление заявками ЦДС. Заявки на выполнения работ на ЭК""",

    'description': """
        Управление заявками ЦДС
    """,

    "author": "Savrasov Mikhail <savrasovmv@tmenergo.ru> ",
    "website": "https://github.com/savrasovmv/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Cds/Request',
    'version': '0.1',
    'application': True,
    'external_dependencies': {
        'python': [
             
            ]},

    # any module necessary for this one to work correctly
    'depends': [
                'base',
                'mail',
                ],

    # always loaded
    'data': [
        # 'views/assets.xml',

        'views/res_users_views.xml',
        'views/res_partner_views.xml',
        'views/cds_views.xml',
        'views/cds_object_views.xml',
        'views/cds_energy_complex_views.xml',
        'views/request_views.xml',
        'views/dashboard_views.xml',
        'views/cds_sequence_data.xml',
        'views/paperformat.xml',
        'views/request_report.xml',
        'views/settings_views.xml',
        'data/inherit_mail_data.xml',
        'data/mail_data.xml',
        'data/activity_type.xml',
        'cron/cron_request_notify_views.xml',
        'security/cds_security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',

    ],
    
    'js': [
        #'static/src/js/toggle_widget.js',
        # 'static/src/js/disabled_copy.js',
    ],

    'css': [
        # 'static/src/scss/adbook.scss',
    ],
}
