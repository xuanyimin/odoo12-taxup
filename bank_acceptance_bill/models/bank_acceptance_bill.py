# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016  德清武康开源软件().
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
import datetime

#开票信息
class BankAcceptanceBill(models.Model):
    _name = 'bank.acceptance.bill'
    _order = "date"
    _description = "Open Bank Acceptance Bill"

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id)
    partner_id = fields.Many2one('res.partner', string='Company', required=True,
                                 default=lambda self: self.env.user.company_id.partner_id)
    name = fields.Many2one('res.partner.bank', u'开票银行',help=u'收此银行开具银承汇票',required=True)
    date = fields.Date(string='开票日期', default=fields.Date.context_today, required=True)
    end_date = fields.Date(string='到期日期', default=fields.Date.context_today, required=True)
    line_ids = fields.One2many('bank.acceptance.bill.line', 'order_id', u'银承明细行', copy=False)
    state = fields.Selection([
        ('draft', '新建'),
        ('pending','开具'),
        ('done', '完成'),
    ], string='状态', index=True, readonly=True, copy=False, default='draft')

    @api.multi
    def begin_date(self, date):
        # 相同供应商的发票。不需要超过90天发票。
        return date-datetime.timedelta(days=90)

    @api.multi
    def invoice_to_bill(self):
        line_done = True
        for line in self.line_ids:

            begin_date = self.begin_date(self.date)
            invoice_ids = self.env['cn.account.invoice'].search(['&','&',('partner_name_in','=',line.name.name),('type','=','in'),('invoice_date','>=',begin_date)], order='invoice_date')
            amount = 0
            for invoice_id in invoice_ids:
                invoice_total = invoice_id.invoice_amount + invoice_id.invoice_tax #发票总金额
                can_use_amount = invoice_total - invoice_id.bank_bill_amount #发票剩余可用额
                if not can_use_amount:
                    continue
                amount += can_use_amount
                if amount >= line.amount:
                    balance = amount - line.amount
                    invoice_id.write({'bank_bill_amount': invoice_total-balance})
                    amount = line.amount
                else:
                    invoice_id.write({'bank_bill_amount': invoice_total})
                line.write({'invoice_amount': amount,
                            'invoice_ids': [(4, invoice_id.id)]})
            if amount != line.amount:
                line_done = False
                line.write({'note':'此次开票少发票，开票金额：%s，发票金额：%s'%(line.amount,round(amount,2))})
            else:
                line.write({'note': '此次开票不少发票，其中发票%s只需使用%s。'%(invoice_id.name,round(invoice_total-balance))})
        if line_done:
            self.state = 'done'
        else:
            self.state = 'pending'


class BankAcceptanceBillLine(models.Model):
    _name = 'bank.acceptance.bill.line'
    _order = "name"
    _description = "Open Bank Acceptance Bill Line"

    order_id = fields.Many2one('bank.acceptance.bill', string='月度银承汇兑', required=True, ondelete='cascade', index=True, copy=False, readonly=True)
    name = fields.Many2one('res.partner', u'供应商',help=u'给谁开票', domain="[('supplier', '=', True)]")
    partner_name =  fields.Char('供应商名字', compute='_compute_partner_name',store=True)
    amount = fields.Float(string='票面金额', required=True,digits=(16,2))
    invoice_ids = fields.Many2many('cn.account.invoice', string='发票',)
    invoice_amount = fields.Float(string='发票金额',digits=(16,2))
    note = fields.Text(string='备注')

    @api.one
    @api.depends('name')
    def _compute_partner_name(self):
        self.partner_name = self.name.name

class cn_account_invoice(models.Model):
    _inherit = 'cn.account.invoice'

    bank_bill_amount = fields.Float(string='已开票金额', digits=(16,2), default=0)