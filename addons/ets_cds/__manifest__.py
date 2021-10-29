# -*- coding: utf-8 -*-
{
    'name': "Диспетчерская служба",

    'summary': """
        Модуль для Диспетчерской службы. Заявки на выполнения работ на ЭК""",

    'description': """
        Диспетчерская служба
    """,

    "author": "Savrasov Mikhail <savrasovmv@tmenergo.ru> ",
    "website": "https://github.com/savrasovmv/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'external_dependencies': {
        'python': [
             
            ]},

    # any module necessary for this one to work correctly
    'depends': [
                'base',
                ],

    # always loaded
    'data': [
        'views/cds_views.xml',
        'views/request_views.xml',
        'views/dashboard_views.xml',
        'views/cds_sequence_data.xml',
        'views/res_partner_views.xml',
        'views/menu.xml',
        'security/security.xml',
        'security/ir.model.access.csv',

    ],
    
    'js': [
        #'static/src/js/toggle_widget.js',
        # 'static/src/js/disabled_copy.js',
    ],

    'css': [
        # 'static/src/scss/adbook.scss',
    ],
}
