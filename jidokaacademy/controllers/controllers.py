# -*- coding: utf-8 -*-
# from odoo import http


# class Jidokaacademy(http.Controller):
#     @http.route('/jidokaacademy/jidokaacademy', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/jidokaacademy/jidokaacademy/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('jidokaacademy.listing', {
#             'root': '/jidokaacademy/jidokaacademy',
#             'objects': http.request.env['jidokaacademy.jidokaacademy'].search([]),
#         })

#     @http.route('/jidokaacademy/jidokaacademy/objects/<model("jidokaacademy.jidokaacademy"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('jidokaacademy.object', {
#             'object': obj
#         })
