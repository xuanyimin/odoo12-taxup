# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016  武康开源软件(宣一敏).
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

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

class Partner(models.Model):
    '''
        在合作伙伴上增加由系统创建标志，用于区别是tax系统反向生成还是别的人员录入，可以作为是否能自动反推的依据
    '''
    _inherit = "res.partner"
    computer_import = fields.Boolean(u'系统创建', default= False)

class ProductTemplate(models.Model):
    _inherit = "product.template"
    '''
        在产品上增加由系统创建标志，用于区别是tax系统反向生成还是别的人员录入，可以作为是否能自动反推的依据
    '''
    computer_import = fields.Boolean(u'系统创建',default= False)
    tax_category_id = fields.Many2one('tax.category', string=u'税收分类')

class tax_category(models.Model):
    _name = 'tax.category'
    '''
        增加税收分类编码，此编码很重要，是开票系统上传国家税务局的数据之一
    '''
    code = fields.Char(u'编号', required=True, help=u'对应SPBM')
    name = fields.Char(u'名称', required=True, help=u'对应SPMC')
    print_name = fields.Char(u'打印名称', help=u'对应SPBMJC')
    superior = fields.Many2one('tax.category', u'上级分类', help=u'上级类别', copy=False)
    can_use = fields.Boolean(u'可使用')
    note = fields.Text(u'备注')
    help = fields.Text(u'说明')
    tax_rate = fields.Char(u'税率', help='因为有可能有多个税率在这里面，所以现在很奇怪')


class ProductCategory(models.Model):
    _inherit = 'product.category'
    tax_category_id = fields.Many2one('tax.category', string=u'税收分类')

