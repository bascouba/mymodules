# -*- coding: utf-8 -*-
from odoo import http


# class Label(http.Controller):
#     @http.route('/label/label/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"
#     @http.route('/label/label/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('label.listing', {
#             'root': '/label/label',
#             'objects': http.request.env['label.label'].search([]),
#         })
#     @http.route('/label/label/objects/<model("label.label"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('label.object', {
#             'object': obj
#         })