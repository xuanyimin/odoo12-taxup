# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
import base64
from lxml import etree
from lxml.etree import CDATA
import re

import sys
import imp
imp.reload(sys)

class ImportTaxConfig(models.TransientModel):
    _name = 'import.tax.config'
    _description = u'导入航天的xml'

    ht_xml = fields.Binary(
        "航天系统中的xml文件", attachment=True, required=True)

    @api.multi
    def import_data(self):
        '''
        读入航天xml文件
        转成list，生成tax_config
        '''
        list = []
        file = base64.b64decode(self.ht_xml).decode('latin-1')
        file2 = re.sub(r'<!\[CDATA\[', '',file)
        file3 = re.sub(r'\]\]>', '',file2)
        parser = etree.HTMLParser(strip_cdata = False)
        tree = etree.HTML(file3.encode('latin-1'), parser=parser)
        for bbox in tree.xpath('//bmxx'):
            app = {}
            for corner in bbox.getchildren():
                try:
                    app[corner.tag] = corner.text
                except:
                    continue
            if app.get('kyzt'):
                list.append(app)
        self.create_tax_category(list)

    @api.multi
    def create_tax_category(self,list):
        spbm = []
        for d in list:
            tax_name = d.get('spmc')
            tax_print = d.get('spbmjc')
            tax_code = d.get('spbm')
            tax_note = d.get('sm')
            tax_help = d.get('gjz')
            tax_rate = d.get('zzssl')
            superior_code = d.get('pid')
            if d.get('hzx') and d.get('hzx') == 'Y':
                tax_can_use = False
            else:
                tax_can_use = True

            old_code = self.env['tax.category'].search([('code','=',tax_code)],limit=1)
            old_superio_code = self.env['tax.category'].search([('code','=',superior_code)],limit=1)
            if old_code:
                old_code.write({
                    'name': tax_name.encode('latin-1').decode('GBK'),
                    'print_name':tax_print and tax_print.encode('latin-1').decode('GBK'),
                    'note': tax_note and tax_note.encode('latin-1').decode('GBK'),
                    'tax_rate': tax_rate,
                    'superior': old_superio_code.id,
                })
                try:
                    old_code.write({
                        'help': tax_help and tax_help.encode('latin-1').decode('GBK'),
                    })
                except:
                    continue
            else:
                app = {}
                tax_id = self.env['tax.category'].create({
                    'name':tax_name.encode('latin-1').decode('GBK'),
                    'code':tax_code,
                    'can_use':tax_can_use,
                    'print_name':tax_print and tax_print.encode('latin-1').decode('GBK'),
                    'note':tax_note and tax_note.encode('latin-1').decode('GBK'),
                    'tax_rate':tax_rate,
                    'superior':old_superio_code.id,
                })
                try:
                    old_code.write({
                        'help': tax_help and tax_help.encode('latin-1').decode('GBK'),
                    })
                except:
                    continue