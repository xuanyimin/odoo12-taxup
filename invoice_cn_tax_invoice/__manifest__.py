# -*- coding: utf-8 -*-
{
    'name': "odoo12的发票生成航天",
    'author': "德清武康开源软件工作室",
    'website': "无",
    'category': '税务处理模块',
    "description":
    '''
                        该模块为发票生成可用于开票软件导入的xml的文件用于导入
    ''',
    'version': '0.01',
    'depends': ['account', 'tax'],
    'data': [
        'view/invoice_tax_xml.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
