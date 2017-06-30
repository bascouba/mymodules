 # -*- coding: utf-8 -*-
 
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
import re


class Product(models.Model):
    _name='product.product'
    _inherit = 'product.product'
    
    matching=fields.Many2many(comodel_name='ses_imagotag.label')
    label_price=fields.Char(compute='get_pos_price', store=True)
    label_discount_percent=fields.Float(digits=(16,2), compute='get_pos_price')
    label_discount_fixed=fields.Float(digits=(16,2), compute='get_pos_price')
    len_matching=fields.Integer(compute="get_len_matching")

    #This trigger doesn't work properly, it triggers for every 
    @api.depends('pricelist_item_ids.price','pricelist_item_ids.percent_price', 'pricelist_item_ids.fixed_price')
    @api.one
    def get_pos_price(self):
        pos_config=self.env['pos.config']
        #TODO: Improve the following getter of the pos's pricelist
        if self.env['ir.config_parameter'].get_param('pos'):
            pos=pos_config.browse(int(re.search(r'\d+', self.env['ir.config_parameter'].get_param('pos')).group()))
            for element in pos :
                for pricelist in element.pricelist_id:
                    self.label_price=pricelist.get_product_price_rule(self,1,False)[0]
                    self.label_discount_percent=self.env['product.pricelist.item'].browse(pricelist.get_product_price_rule(self,1,False)[1]).percent_price
                    if self.env['product.pricelist.item'].browse(pricelist.get_product_price_rule(self,1,False)[1]).fixed_price!=0:
                        self.label_discount_fixed=(self.list_price - self.env['product.pricelist.item'].browse(pricelist.get_product_price_rule(self,1,False)[1]).fixed_price)

    @api.one
    def get_len_matching(self):
        self.len_matching=len(self.matching)
        
    
class Product(models.Model):
    _name='product.template'
    _inherit='product.template'
    
    matching=fields.Many2many(comodel_name='ses_imagotag.label', compute="get_matching")
    len_matching_template=fields.Integer(compute="get_len_matching_template")
    
    @api.multi
    def get_matching(self):
        for record in self:
            record.matching=[]
            for product in record.product_variant_ids:
                record.matching+=product.matching
    
    @api.one
    def get_len_matching_template(self):
        self.len_matching_template=len(self.matching)    
        
    @api.multi
    def action_view_matchings(self):
        self.ensure_one()
        action = self.env.ref('label.action_product_label_list')

        return {
            'name': action.name,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'res_model': action.res_model,
            'domain': [('products.product_tmpl_id', '=', self.id)],
        }
        
#     @api.one
#     def action_link_to_label(self):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Labels to be linked',
#             'res_model': self._name,
#             'view_mode': 'form',
#             'view_type': 'form',
#             'target': 'current',
#             'flags': {'initial_mode': 'edit'}
#         }