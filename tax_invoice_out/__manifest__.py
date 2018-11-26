# -*- coding: utf-8 -*-
{
    'name': "GOODERP 税务模块-销项发票",
    'author': "德清武康开源软件工作室",
    'website': "无",
    'category': '税务模块-销项发票',
    "description":
    '''
        模块为从金税系统导出开票内容，导入系统后，为系统发票与。
    ''',
    'version': '11.11',
    'depends': ['cn_account_invoice'],
    'data': [
        'view/tax_invoice_out_view.xml',
        'view/tax_invoice_out_action.xml',
        'view/tax_invoice_out_menu.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
}
