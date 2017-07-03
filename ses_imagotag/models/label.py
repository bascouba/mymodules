# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, except_orm, Warning, RedirectWarning
from xml.etree import ElementTree
from xml.etree.cElementTree import XML
from random import randint
from odoo.osv import osv
from odoo.osv import orm
import logging
import sys
import urllib2
import requests
import base64
import re


class Label(models.Model):
	_name='ses_imagotag.label'
	
	_logger = logging.getLogger(__name__)
	
	@api.multi
	def name_get(self):
	    res = []
	    for asset in self:
	        display_name = []
	        res.append((asset.id,
	                    asset.description or asset.real_id))
	    return res
	
	real_id=fields.Char(required=True, size=8, string="Label ID", help="The ID written physically on the label")
	type=fields.Char(compute="_get_type_and_status", help="Size and model of the display")
	size=fields.Char(compute="_get_type_and_status", help="Size of the display in pixels")
	status=fields.Char(compute="_get_type_and_status", help="Show if the label is linked to the access point.      If it is offline for more than 30min, the label is unreachable.     If it is unregistered, please delete and recreate the label")
	description=fields.Char(required=False, size=20, string="Name", help="You can set a nickname to the label to recognize it faster")
	image=fields.Binary(compute="_get_last_image_loaded", string="", help="The image that is supposed to be on the label when store opens")
	status_color=fields.Integer(compute="_check_color")
	is_created=fields.Boolean('Created')
	need_update=fields.Boolean(compute="_need_update", default="False", store=True)
	
	# Matching Attributes 
	png=fields.Binary(string="Additional image",help="Add a .png that will be displayed on the label (depends on the template). The label can only display red, white and black pixels : if you want a good rendering of your image, you may have to rework it (with dithering and resizing to fit the template)", required=False)
	task_id=fields.Char()
	task_status=fields.Char(compute="_get_status_task", string="Task Status")
	products=fields.Many2many(comodel_name='product.product', string="Article", help="The products you want to link to be displayed on the label")
	len_products=fields.Integer(compute='_get_len_products', store=True)
	template=fields.Many2one(comodel_name='ses_imagotag.template', help="The template that defines the way informations of the products will be displayed")
	preview=fields.Binary(compute="_get_preview", string="Preview", help="Preview of the products with the actual template")
	
	
	# =============== #
	# Compute Methods #
	# =============== #
	
	@api.multi
	@api.depends('products')
	def _get_len_products(self):  
		for label in self: 
			label.len_products=0
			for product in label.products:
				label.len_products+=1
				
	
	@api.one
	@api.depends('real_id')
	def _get_type_and_status(self) :
		for location in self:
			if location.real_id:
				response=requests.get('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/labelinfo/'+location.real_id)
				if response:
					root=XML(response.text)
					for resp in root.iter('ConnectionStatus'):
						location.status=resp.text
				else:
					location.type="UNKNOWN"
					location.status="UNREGISTERED"
				response=requests.get('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/labelinfo/type/'+location.real_id)
				if response:
					root=XML(response.text)
					for resp in root.iter('Name'):
						location.type=resp.text
					for resp in root.iter('DisplayWidth'):
						location.size=resp.text
					for resp in root.iter('DisplayHeight'):
						location.size+="*"+resp.text
				else:
					location.type="UNKNOWN"

	@api.one
	@api.depends('task_id')
	def _get_status_task(self):
		for location in self:
			if location.task_id:
				response=requests.get('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/transaction/'+location.task_id+'/status')
				if response:
					root=XML(response.text)
					for resp in root.iter('TransactionStatusInfo'):
						if resp.get('failed')=="true":
							location.task_status="FAILED"
						elif resp.get('finished')=="true":
							location.task_status="FINISHED"
						else:
							location.task_status="WAITING"
							
	@api.multi
	@api.depends('status', 'task_status')
	def _check_color(self):
		for record in self:
			record.status_color = 1
			if record.status == 'ONLINE' and (record.task_status=='FINISHED' or record.task_status=='WAITING' or record.task_status==False):
				record.status_color = 6
			elif record.status == 'OFFLINE' or record.task_status=='FAILED':
				record.status_color = 2				
	
	@api.depends('task_id')
	@api.multi
	def _get_last_image_loaded(self):
		for label in self:
			task_id=""
			labelupdatestatus=False
 			if label.task_id:
			 	labelupdatestatus=requests.get('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/updatestatus/transaction/'+label.task_id)
				if labelupdatestatus:
 					root=XML(labelupdatestatus.text)
 				 	for update in root.iter('UpdateStatus'):
 					 	task_id=update.get('id')	
 		 	 	label.image=label._get_image_from_task(task_id)
 		 	else:
 		 		label.image=False
 		 	
	@api.one
	def _get_image_from_task(self, task_id):
		if task_id!="":
			response=requests.get('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/updatestatus/'+task_id+'/image')  		
  			return base64.b64encode(response.content)
  		else:
  			return False
  		
	@api.one	
	@api.depends(
		'png',
		'products',
		'template',
		'products.name',
		'products.list_price',
		'products.label_price',
		'products.product_tmpl_id.name', 
		'products.product_tmpl_id.image', 
		'products.product_tmpl_id.description_sale', 
		'products.product_tmpl_id.description',
		'products.attribute_value_ids.name', 
		'products.attribute_value_ids.price_ids.price_extra', 
		'products.attribute_value_ids.price_ids.product_tmpl_id',
		)
	def _need_update(self):
		self.need_update=True

	@api.multi
	def _update_esl(self):
		for label in self.search([]):
			if label.len_products!=0 and label.need_update==True:
				response=requests.post('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/task', data=label._build_task_body().encode('utf-8'), headers={'Content-Type':'application/xml'})
				root=XML(response.text)
				for transaction in root.iter('Transaction'):
					label.task_id=transaction.get('id')
				label.need_update=False
				
	@api.model
	def _build_task_body(self):
		xmlbody=""
		xmlbody+="<TaskOrder title='Update ESLs from Odoo'>"
		if self.env['ses_imagotag.template'].browse(int(re.search(r'\d+', self.env['ir.config_parameter'].get_param('template_gestion')).group())):
			xmlbody+=self._xml_content(self.products,self.env['ses_imagotag.template'].browse(int(re.search(r'\d+', self.env['ir.config_parameter'].get_param('template_gestion')).group())),1)
		xmlbody+=self._xml_content(self.products,self.template,0)
		xmlbody+="</TaskOrder>"
		return xmlbody
			
	@api.model
	def _xml_content(self,products,template,page):
		xmlbody="<TemplateTask page='"+str(page)+"' preload='true' template='"
		xmlbody+=template.name+"'"
		xmlbody+=" labelId='"+self.real_id+"' taskPriority='NORMAL' externalId='8069'>"
		if template.multi:
			xmlbody+="<articles>"
		if self.png and template.multi:
			xmlbody+="""<field key='png' value=" """+self.png+""" "/>"""
		for product in products:
			xmlbody+="<article>"
			if self.png and template.multi==False:
				xmlbody+="""<field key='png' value=" """+self.png+""" "/>"""
			xmlbody+="""<field key='name' value='"""+product.name+"""'/>"""
			xmlbody+="<field key='price' value='"+str('%.2f' % float(product.label_price) or '%.2f' % float(product.list_price))+"'/>"
			if product.label_discount_percent!=0:
				xmlbody+="<field key='base_price' value='"+str('%.2f' % float(product.list_price))+"'/>"
				xmlbody+="<field key='discount_percent' value='"+str(product.label_discount_percent)+"'/>"
			if product.label_discount_fixed!=0:
				xmlbody+="<field key='base_price' value='"+str('%.2f' % float(product.list_price))+"'/>"
				xmlbody+="<field key='discount_fixed' value='"+str(product.label_discount_fixed)+"'/>"
			xmlbody+="<field key='image' value='"+(product.image or "")+"'/>"
			xmlbody+="""<field key='stock' value=" """+str(product.qty_available)+""" "/>"""
			if product.description:
				xmlbody+="""<field key='description' value=" """+product.description+""" "/>"""
			if product.description_sale:
				xmlbody+="""<field key='description_sale' value=" """+product.description_sale+""" "/>"""
			if product.attribute_value_ids:
				xmlbody+="""<field key='attributes' value=" """				
				for attribute in product.attribute_value_ids:
					xmlbody+=attribute.name+" "
				xmlbody+=""" "/>"""
			if hasattr(product.product_tmpl_id, 'website_url') and self.env['ir.config_parameter'].get_param('website'):
				xmlbody+="<field key='url' value='"+self.env['ir.config_parameter'].get_param('website')+product.product_tmpl_id.website_url+"'/>"
			xmlbody+="</article>"
		if template.multi:
			xmlbody+="</articles>"
		xmlbody+="</TemplateTask>"
		return xmlbody
						
	@api.one
 	@api.depends('products','template','png')
	def _get_preview(self):
		if self.products and self.template:
	 		response=requests.post('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/task/preview/image', data=self._xml_content(self.products,self.template,0).encode('utf-8'), headers={'Content-Type':'application/xml'})
	 		if response:
	 			self.preview=base64.b64encode(response.content)
			else:
				self.preview=False
		else:
			self.preview=False		
			
	@api.multi
	def _switch_page(self, page):
		for label in self.search([]):
			if label.len_products!=0:
				response=requests.post('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/task', data=label._build_switch_page(page).encode('utf-8'), headers={'Content-Type':'application/xml'})

	def _build_switch_page(self, page):
		return '<TaskOrder title="Switch Page to page '+str(page)+' from Odoo"><SwitchPageTask page="'+str(page)+'" labelId="'+self.real_id+'" taskPriority="NORMAL" externalId="8069"/></TaskOrder>'

	@api.one
	def _register_label(self, Label_id):
		response=requests.post('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/label', data='<LabelList><Label id=\"'+Label_id+'\"/></LabelList>',headers={'Content-Type':'application/xml'})
		
	@api.one
	def _unregister_label(self, Label_id):
		response=requests.delete('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/label/'+Label_id)
				
	def is_registered(self, label):
		response=requests.get('http://'+self.env['ir.config_parameter'].get_param('core_appliance_ip')+':8001/service/labelinfo/'+label)
		if response.status_code==200:
			return True
		else:
			return False
		
	@api.model
	def create(self, vals):	
		if len(vals['real_id'])!=8:
			My_error_Msg = 'Label ID must have 8 characters'
			raise osv.except_osv(("Error!"), (My_error_Msg))
		else:
			vals['is_created'] = True
			if self.is_registered(vals['real_id']):
				rec=super(Label,self).create(vals)
			else:
				rec=super(Label, self).create(vals)
				rec._register_label(vals['real_id'])
			return rec

	@api.multi
	def write(self, vals):
			rec=super(Label,self).write(vals)
			for record in self:
				if vals.get('template'):
					record.template.set_preview(record.preview)
			return {
			        'type': 'ir.actions.act_window',
			        'res_model': 'ses_imagotag.label',
			        'view_mode': 'tree,form',
			        'view_type': 'form',
			        'context':self._context.copy()
			}
		
	@api.multi
	def unlink(self):
		for labeltodelete in self:
			if labeltodelete.real_id:
				self._unregister_label(labeltodelete.real_id)
		return super(Label, self).unlink()
	
	# ============================
	# Views Transition and Actions
	# ============================
	
	def form_to_matching(self):
		view_id = self.env['ir.model.data'].get_object('ses_imagotag','label_matching_form')
		return {
	        'type': 'ir.actions.act_window',
	        'res_model': 'ses_imagotag.label',
	        'view_id': view_id.id,
 	        'res_id': self.id,
 	      	'view_mode': 'form',
 	       	'view_type': 'form',
			'flags': {'initial_mode': 'edit'},
			'context': {}
	    }
	
	def new_match(self):
		context=self._context.copy()

		if context.get('active_ids') and len(context.get('active_ids'))!=1:
 			self.template=self.env['ses_imagotag.template'].search(['&','|',('size','like',self.size),('dyn','=',True),('multi','=',True)])[0]
			self.products=[(6,0,context.get('active_ids'))] 
		else:
			self.products=[(6,0,[context.get('active_id')])] 
 			self.template=self.env['ses_imagotag.template'].search(['&','|',('size','like',self.size),('dyn','=',True),('multi','=',False)])[0]
		
		return {
            'name':_("Save a new matching"),
            'view_mode': 'form',
			'view_type': 'form',
            'res_model': 'ses_imagotag.label',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': '[]',
			'flags': {'initial_mode': 'edit',},
            }
		
	## Same as previous but from product.template object ##
	
	def new_match_template(self):
		context=self._context.copy()
		if context.get('active_ids') and len(context.get('active_ids'))!=1:
			product_ids=[]
			for product_template in context.get('active_ids'):
				product_ids+=[self.env['product.template'].browse(product_template).product_variant_id.id]
 			self.template=self.env['ses_imagotag.template'].search(['&','|',('size','like',self.size),('dyn','=',True),('multi','=',True)])[0]
			self.products=[(6,0,product_ids)] 
		else:
			self.products=[(6,0,[self.env['product.template'].browse(context.get('active_id')).product_variant_id.id])] 
 			self.template=self.env['ses_imagotag.template'].search(['&','|',('size','like',self.size),('dyn','=',True),('multi','=',False)])[0]
		
		return {
            'name':_("Save a new matching"),
            'view_mode': 'form',
			'view_type': 'form',
            'res_model': 'ses_imagotag.label',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': '[]',
			'flags': {'initial_mode': 'edit',},
            }	
		
	@api.one
	@api.constrains('template', 'len_products')
	def _check_multi_products(self):
		if self.template.multi == False and self.len_products>1:
			raise osv.except_osv(("Error!"),"This template can't handle more than one product")

	_sql_constraints = [
        ('real_id_uniq', 'unique (real_id)', "The Label can't be registered twice"),
    ]

	