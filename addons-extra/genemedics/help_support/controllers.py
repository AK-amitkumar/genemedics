# -*- coding: utf-8 -*-
from openerp import http

# class HelpSupport(http.Controller):
#     @http.route('/help_support/help_support/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/help_support/help_support/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('help_support.listing', {
#             'root': '/help_support/help_support',
#             'objects': http.request.env['help_support.help_support'].search([]),
#         })

#     @http.route('/help_support/help_support/objects/<model("help_support.help_support"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('help_support.object', {
#             'object': obj
#         })