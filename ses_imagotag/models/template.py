# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import requests
from xml.etree.cElementTree import XML


class Template(models.Model):
	_name='ses_imagotag.template'
	_rec_name = 'description'
	
	
	name=fields.Char(required=True, string="File", Help="Name of the template file present on the server")
	description=fields.Char(required=True, string="Name", help="The name you will see (make it as descriptive as possible)")
	type=fields.Char(compute="_get_type_template", store=True, help="Size and model of the displays supported")
	size=fields.Char(compute="_get_type_template", store=True, help="Size of the displays supported in pixels")
	multi=fields.Boolean(string="Multi-Products", compute="_get_type_template", store=True, help="Says if the template can handle more than one product")
	dyn=fields.Boolean(compute="_get_type_template", store=True, help="The template can handle every kind of display")
	preview=fields.Binary(help="Preview of the template, is shown after one matching created with this template")
	
	label=fields.One2many(comodel_name='ses_imagotag.label', inverse_name='template')
	config=fields.One2many(comodel_name='ses_imagotag.config.settings', inverse_name='template_gestion')
	
	
	@api.depends('name')
	@api.one
	def _get_type_template(self):
		if self.name:
			self.type=""
			self.size=""
			if self.env['ir.config_parameter'].get_param('core_appliance_ip'):
				response=requests.get('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/template/'+self.name)
				if "articles" in response.text:
					self.multi=True
				else:
					self.multi=False
				root=XML(response.text.encode('utf-8'))
				for resp in root.iter('image'):
					count=0
					if resp.get('width')=="152" and resp.get('height')=="152":
						self.type+="G1 1.6 red "
						self.size+="152*152 "
						count+=1
					if resp.get('width')=="212" and resp.get('height')=="104":
						self.type+="G1 2.2 red "
						self.size+="212*104 "
						count+=1
					if resp.get('width')=="296" and resp.get('height')=="152":
						self.type+="G1 2.6 red "
						self.size+="296*152 "
						count+=1
					if resp.get('width')=="264" and resp.get('height')=="176":
						self.type+="G1 2.7 red "
						self.size+="264*176 "
						count+=1
					if resp.get('width')=="400" and resp.get('height')=="300":
						self.type+="G1 4.2 red G1 4.4 red "
						self.size+="400*300 "
						count+=1
					if resp.get('width')=="480" and resp.get('height')=="176":
						self.type+="G1 4.5 red "
						self.size+="480*176 "
						count+=1
					if resp.get('width')=="600" and resp.get('height')=="448":
						self.type+="G1 6.0 red "
						self.size+="600*448 "
						count+=1
					if resp.get('width')=="480" and resp.get('height')=="800":
						self.type+="G1 7.4 red "
						self.size+="480*800 "
						count+=1
					if resp.get('width')=="768" and resp.get('height')=="960":
						self.type+="G1 12.2 red "
						self.size+="768*960 "
						count+=1
					if count==0 or count==9:
						self.type="Dynamic"
						self.size=str(resp.get('width'))+"*"+str(resp.get('height'))
						self.dyn=True
			else:
				self.dyn=True

    
	def set_preview(self, image):
		self.preview=image
				
		
	_sql_constraints = [
        ('name_uniq', 'unique (name)', "The Template can't be registered twice"),
        ('description_type_uniq', 'unique (description,type)',"A Template for this type of label already exists with this name"),
    ]
	
