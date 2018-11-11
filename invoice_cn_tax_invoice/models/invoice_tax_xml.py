# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016  德清武康开源软件().
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundaption, either version 3 of the
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
import base64
from odoo.exceptions import UserError
from lxml import etree



class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    #把发票生成可在航天系统导入的xml文件，放入附件
    attachment_number = fields.Integer(compute='_compute_attachment_number', string=u'附件号')

    @api.multi
    def action_get_attachment_view(self):
        res = self.env['ir.actions.act_window'].for_xml_id('base', 'action_attachment')
        res['domain'] = [('res_model', '=', 'account.invoice'), ('res_id', 'in', self.ids)]
        res['context'] = {'default_res_model': 'account.invoice', 'default_res_id': self.id}
        return res

    @api.multi
    def _compute_attachment_number(self):
        attachment_data = self.env['ir.attachment'].read_group(
            [('res_model', '=', 'account.invoice'), ('res_id', 'in', self.ids)], ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
        for expense in self:
            expense.attachment_number = attachment.get(expense.id, 0)

    @api.multi
    def create_tax_xml(self):
        # 处理XML头
        invoice_top = 100000
        amount = 0
        number = 1
        line_number = 0
        Kp = etree.Element('Kp')
        Version = etree.SubElement(Kp, 'Version')
        Version.text = '3.0'
        Fpxx = etree.SubElement(Kp, 'Fpxx')
        Fp = self.tax_top(number,Fpxx)
        for line in self.invoice_line_ids:
            line_number += 1
            if amount < invoice_top:
                amount += line.price_subtotal
                self.tax_line(line, line_number,Fp)
            else:
                amount = line_number = 0
                number += 1
                Fp = self.tax_top(number,Fpxx)
                amount += line.price_subtotal
                self.tax_line(line, line_number,Fp)
        tree = etree.ElementTree(Kp)
        tree.write('./xml/tax_invoice.xml', pretty_print=True, xml_declaration= True, encoding='GBK')
        f = open('./xml/tax_invoice.xml','rb')
        self.env['ir.attachment'].create({
            'datas': base64.b64encode(f.read()),
            'name': '航天发票xml',
            'datas_fname': '%s航天xml.xml'%(self.number),
            'res_model': 'account.invoice',
            'res_id': self.id,
        })


    @api.multi
    def tax_top(self,number,Fpxx):
        Zsl = etree.SubElement(Fpxx, 'Zsl')  # 单据数量
        Zsl.text = str(number)
        state = self.partner_id.state_id.name + self.partner_id.city + self.partner_id.street2 + self.partner_id.street #公司地址
        bank = self.partner_id.bank_ids and self.partner_id.bank_ids.bank_id.name or ''
        bank_number = self.partner_id.bank_ids and self.partner_id.bank_ids.acc_number or ''
        # 发票头
        Fpsj = etree.SubElement(Fpxx, 'Fpsj')
        Fp = etree.SubElement(Fpsj, 'Fp')
        Djh = etree.SubElement(Fp, 'Djh')  # 单据号
        Djh.text = '%s' % (self.id)
        Spbmbbh = etree.SubElement(Fp, 'Spbmbbh')  # 商品编码版本号
        Spbmbbh.text = '19.0'
        Hsbz = etree.SubElement(Fp, 'Hsbz')  # 含税标志
        Hsbz.text = u'0'
        Sgbz = etree.SubElement(Fp, 'Sgbz')  # 含税标志
        Hsbz.text = u'0'
        Gfmc = etree.SubElement(Fp, 'Gfmc')  # 购方名称
        Gfmc.text = self.partner_id.name
        Gfsh = etree.SubElement(Fp, 'Gfsh')  # 购方税号
        Gfsh.text = self.partner_id.vat
        Gfdzdh = etree.SubElement(Fp, 'Gfdzdh')  # 购方地址电话
        Gfdzdh.text = '%s %s' % (state,self.partner_id.phone or self.partner_id.mobile)
        Gfyhzh = etree.SubElement(Fp, 'Gfyhzh')  # 购方银行帐号
        Gfyhzh.text = '%s %s' % (bank, bank_number)
        Skr = etree.SubElement(Fp, 'Skr')  # 收款人
        Skr.text = u''
        Fhr = etree.SubElement(Fp, 'Fhr')  # 复核人
        Fhr.text = u''
        Bz = etree.SubElement(Fp, 'Bz')  # 备注
        Bz.text = str(self.comment or '')
        return(Fp)


    @api.multi
    def tax_line(self,line,line_number,Fp):
        Spxx = etree.SubElement(Fp, 'Spxx')
        Sph = etree.SubElement(Spxx, 'Sph')
        Kce = etree.SubElement(Sph, 'Kce')  # 扣除额
        Kce.text = ''
        Spbm = etree.SubElement(Sph, 'Spbm')  # 商品编码
        if line.product_id.tax_category_id:
            good_tax_number = line.product_id.tax_category_id.code
        elif line.product_id.categ_id.tax_category_id:
            good_tax_number = line.product_id.categ_id.tax_category_id.code
        else:
            raise UserError(_('请给此商品或商品分类上设置税收分类编码'))
        Spbm.text = good_tax_number
        Dj = etree.SubElement(Sph, 'Dj')  # 单价
        Dj.text = str(round(line.price_subtotal/line.quantity,6))
        Spmc = etree.SubElement(Sph, 'Spmc')  # 商品名称
        Spmc.text = line.product_id.name
        Ggxh = etree.SubElement(Sph, 'Ggxh')  # 规格型号
        Ggxh.text = ''
        Slv = etree.SubElement(Sph, 'Slv')  # 税率
        Slv.text = str(line.invoice_line_tax_ids.amount/100)
        Xh = etree.SubElement(Sph, 'Xh')  # 序号
        Xh.text = str(line_number)
        Lslbz = etree.SubElement(Sph, 'Lslbz')  # 零标识，0出口退税，1免税
        Lslbz.text = ''
        Syyhzcbz = etree.SubElement(Sph, 'Syyhzcbz')  # 优惠政策标识：0不使用，1使用
        Syyhzcbz.text = ''
        Sl = etree.SubElement(Sph, 'Sl')  # 数量
        Sl.text = str(line.quantity)
        Je = etree.SubElement(Sph, 'Je')  # 金额
        Je.text = str(line.price_subtotal)
        Yhzcsm = etree.SubElement(Sph, 'Yhzcsm')  # 优惠政策说明
        Yhzcsm.text = ''
        Qyspbm = etree.SubElement(Sph, 'Qyspbm')  # 企业商品编码
        Qyspbm.text = line.product_id.default_code
        Jldw = etree.SubElement(Sph, 'Jldw')  # 计量单位
        Jldw.text = line.product_id.uom_id.name
