# -*- coding: utf-8 -*-
{
    'name': "GOODERP 税务模块",
    'author': "德清武康开源软件工作室",
    'website': "无",
    'category': '税务处理模块',
    "description":
    '''
                        该模块为税务基础模块
    ''',
    'version': '0.01',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'security/tax_security.xml',
        'view/tax_config_view.xml',
        'wizard/import_tax_config_views.xml',
        'view/tax_config_action.xml',
        'view/tax_config_menu.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
