# -*- coding: utf-8 -*-

from odoo import fields, models
import logging
import requests
import re
from xml.etree import ElementTree
from xml.etree.cElementTree import XML

_logger = logging.getLogger(__name__)

class LabelConfigSettings(models.TransientModel):

	_name = 'label.config.settings'
	_inherit = 'res.config.settings'
	
	core_appliance_ip = fields.Char('Core Appliance IP', default="localhost", required=True, help="IP Address of the imagotag server. !! This parameter has to be set before registering labels on Odoo !!")
	website=fields.Char('Website Domain', help="Website domain where the products are sold")
	
	pos=fields.Many2one(comodel_name='pos.config', string="Point of Sale", delegate=True)
	template_gestion=fields.Many2one(comodel_name='label.template', string='Template Inventory', delegate=True)
# 	store_open=fields.Boolean(help="Used to check if store is open or close to choose template", default=True)
	

	def get_default_core_appliance_ip(self, fields):
		core_appliance_ip = self.env['ir.config_parameter'].get_param('core_appliance_ip')
		return dict(core_appliance_ip=core_appliance_ip)
	
	def get_default_website(self, fields):
		website = self.env['ir.config_parameter'].get_param('website')
		return dict(website=website)

   	def get_default_template_gestion(self, fields):
  		template_gestion = self.env['ir.config_parameter'].get_param('template_gestion')
  		return dict(template_gestion=template_gestion)
	
 	def get_default_pos(self, fields):
		pos = self.env['ir.config_parameter'].get_param('pos')
		return dict(pos=pos)


	def set_default_core_appliance_ip(self):
		self.env['ir.config_parameter'].set_param('core_appliance_ip', (self.core_appliance_ip or '').strip(), groups=['base.group_system'])
		
	def set_default_website(self):
		self.env['ir.config_parameter'].set_param('website', (self.website or '').strip(), groups=['base.group_system'])
	
	def set_default_template_gestion(self):
		self.env['ir.config_parameter'].set_param('template_gestion', (self.template_gestion.id or ''), groups=['base.group_system'])
		
	def set_default_pos(self):
		self.env['ir.config_parameter'].set_param('pos', (self.pos.id or ''), groups=['base.group_system'])
		
		