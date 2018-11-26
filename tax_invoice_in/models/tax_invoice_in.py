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
import odoo.addons.decimal_precision as dp
import xlrd
import base64
import datetime
import time
import random

#每月进项发票
class tax_invoice_in(models.Model):
    _name = 'tax.invoice.in'
    _order = "name"

    name = fields.Date(string='导入日期', default=fields.Date.context_today, required=True)
    line_ids = fields.One2many('cn.account.invoice', 'invoice_in_id', u'进项发票明细行',copy=False)
    tax_amount = fields.Float(string=u'合计可抵扣税额', store=True, readonly=True,
                        compute='_compute_tax_amount', track_visibility='always',
                        digits=dp.get_precision('Amount'))

    @api.multi
    @api.depends('line_ids.invoice_tax', 'line_ids.is_deductible')
    def _compute_tax_amount(self):
        '''当明细行的税额或是否抵扣改变时，改变可抵扣税额合计'''
        total = 0
        for line in self.line_ids:
            if line.is_deductible:
                total = total + 0
            else:
                total = total +line.invoice_tax
        self.tax_amount = total

    #引入EXCEL的wizard的button
    @api.multi
    def button_excel(self):
        return {
            'name': u'引入excel',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'create.cn.account.invoice.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    # @api.multi
    # def write(self, vals):
    #     res = super(tax_invoice_in, self).write(vals)
    #     return res

#用excel导入认证系统的EXCEL生成月认证发票
class create_cn_account_invoice_wizard(models.TransientModel):
    _name = 'create.cn.account.invoice.wizard'
    _description = 'Tax Invoice Import'

    type = fields.Selection([
        ('ztsm', '中天易税认证平台扫描认证'),
        ('ztgx', '中天易税认证平台钩选认证'),
        ('gx', '增值税勾选平台'),], string='导出源',)
    excel = fields.Binary(u'导入认证系统导出的excel文件',)

    @api.multi
    def create_zt_cn_account_invoice(self):
        if not self.env.context.get('active_id'):
            return
        invoice_in = self.env['tax.invoice.in'].browse(self.env.context.get('active_id'))
        """
        通过Excel文件导入信息到cn.account.invoice
        """
        if not invoice_in:
            return {}
        xls_data = xlrd.open_workbook(file_contents=base64.decodestring(self.excel))
        table = xls_data.sheets()[0]
        ncows = table.nrows
        ncols = 0
        colnames =  table.row_values(0)
        list =[]
        #数据读入，过滤没有开票日期的行
        for rownum in range(1,ncows):
            row = table.row_values(rownum)
            if row:
                app = {}
                for i in range(len(colnames)):
                   app[colnames[i]] = row[i]
                if app.get(u'开票日期'):
                    list.append(app)
                    ncols += 1

        #数据处理
        in_xls_data = {}
        for data in range(0,ncols):
            in_xls_data = list[data]
            invoice_code = in_xls_data.get(u'发票代码')
            partner_name = in_xls_data.get(u'销方名称')
            self.env['cn.account.invoice'].create({
                'type': 'in',
                'partner_name_in': partner_name,
                'partner_code_in': str(in_xls_data.get(u'销方税号')),
                'invoice_code': str(invoice_code),
                'name': str(in_xls_data.get(u'发票号码')),
                'invoice_amount': float(in_xls_data.get(u'金额')),
                'invoice_tax': float(in_xls_data.get(u'税额')),
                'invoice_date': self.excel_date(in_xls_data.get(u'开票日期')),
                'invoice_confirm_date': self.excel_date(in_xls_data.get(u'认证时间') or in_xls_data.get(u'确认时间')),
                'invoice_type': 'zy',
                'invoice_in_id': invoice_in.id or '',
                'tax_rate': float(in_xls_data.get(u'税额'))/float(in_xls_data.get(u'金额'))*100,
                'is_verified': False,
                })

    @api.multi
    def create_cn_account_invoice(self):
        if not self.env.context.get('active_id'):
            return
        invoice_in = self.env['tax.invoice.in'].browse(self.env.context.get('active_id'))
        """
        通过Excel文件导入信息到cn.account.invoice
        """
        if not invoice_in:
            return {}
        xls_data = xlrd.open_workbook(file_contents=base64.decodestring(self.excel))
        table = xls_data.sheets()[0]
        ncows = table.nrows
        ncols = 0
        colnames = table.row_values(2)
        list = []
        # 数据读入，过滤没有开票日期的行
        for rownum in range(3, ncows):
            row = table.row_values(rownum)
            if row:
                app = {}
                for i in range(len(colnames)):
                    app[colnames[i]] = row[i]
                if app.get(u'开票日期'):
                    list.append(app)
                    ncols += 1

        # 数据处理
        in_xls_data = {}
        for data in range(0, ncols):
            in_xls_data = list[data]
            invoice_code = in_xls_data.get(u'发票代码')
            partner_name = in_xls_data.get(u'销方名称')
            self.env['cn.account.invoice'].create({
                'type': 'in',
                'partner_name_in': partner_name,
                'partner_code_in': str(in_xls_data.get(u'销方税号')),
                'invoice_code': str(invoice_code),
                'name': str(in_xls_data.get(u'发票号码')),
                'invoice_amount': float(in_xls_data.get(u'金额')),
                'invoice_tax': float(in_xls_data.get(u'税额')),
                'invoice_date': self.excel_date(in_xls_data.get(u'开票日期')),
                'invoice_confirm_date': invoice_in.name,
                'invoice_type': 'zy',
                'invoice_in_id': invoice_in.id or '',
                'tax_rate': float(in_xls_data.get(u'税额')) / float(in_xls_data.get(u'金额')) * 100,
                'is_verified': False,
            })

    def excel_date(self,data):
        #将excel日期改为正常日期
        if type(data) in (int,float):
            year, month, day, hour, minute, second = xlrd.xldate_as_tuple(data,0)
            py_date = datetime.datetime(year, month, day, hour, minute, second)
        else:
            py_date = data
        return py_date

#增加按月进项发票
class cn_account_invoice(models.Model):
    _inherit = 'cn.account.invoice'
    _description = u'中国发票'
    _rec_name='name'

    invoice_in_id = fields.Many2one('tax.invoice.in', u'对应入帐月份', index=True, copy=False, readonly=True)
