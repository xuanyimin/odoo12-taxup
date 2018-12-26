# -*- coding: utf-8 -*-
{
    'name': "GOODERP 银行模块-银承汇票开具",
    'author': "德清武康开源软件工作室",
    'website': "无",
    'category': '银行承况汇票',
    "description":
    '''
        银行承况汇票开具时需要提供发票，并在发票上盖章在某年某月某日在某行开银承多少钱。
        有时一张发票会在二家银行开具银承汇票，管理上需要一个记录，并快速找到合适的发票。
    ''',
    'version': '0.01',
    'depends': ['cn_account_invoice'],
    'data': [
        'security/ir.model.access.csv',
        'view/bank_acceptance_bill_view.xml',
        'view/bank_acceptance_bill_action.xml',
        'view/bank_acceptance_bill_menu.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
