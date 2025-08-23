# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseExtension(http.Controller):
#     @http.route('/purchase_extension/purchase_extension', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_extension/purchase_extension/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_extension.listing', {
#             'root': '/purchase_extension/purchase_extension',
#             'objects': http.request.env['purchase_extension.purchase_extension'].search([]),
#         })

#     @http.route('/purchase_extension/purchase_extension/objects/<model("purchase_extension.purchase_extension"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_extension.object', {
#             'object': obj
#         })

