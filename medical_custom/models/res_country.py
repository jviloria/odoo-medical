# -*- coding: utf-8 -*-
# #############################################################################
#
# Tech-Receptives Solutions Pvt. Ltd.
# Copyright (C) 2004-TODAY Tech-Receptives(<http://www.techreceptives.com>)
# Special Credit and Thanks to Thymbra Latinoamericana S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################
from openerp import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class CountryCity(models.Model):
    _description="State city"
    _name = 'res.country.state.city'
    _order = 'code'

    @api.model
    def _get_default(self):
        #TODO:Configuración del code por defecto
        city = self.search([('code','=','001')])    #MONTERIA
        return city or False

    state_id = fields.Many2one('res.country.state', 'State',
        required=True)
    name = fields.Char('City Name', required=True, 
                        help='Administrative divisions of a state.')
    code = fields.Char('City Code', size=3,
        help='The city code in max. three chars.', required=True)


# class CountryCity(osv.osv):
#     _description="State city"
#     _name = 'res.country.state.city'

#     #@api.model
#     def _get_default(self, cr, uid, context=None):
#         #TODO:Configuración del code por defecto
#         city = self.search(cr, uid,[('code','=','001')])
#         if city:
#             return city
#         else:
#             return False

#     _columns = {
#         'state_id': fields.many2one('res.country.state', 'State',
#             required=True),
#         'name': fields.char('City Name', required=True, 
#                             help='Administrative divisions of a state.'),
#         'code': fields.char('City Code', size=3,
#             help='The city code in max. three chars.', required=True),
#     }
#     _order = 'code'

#     #name_search = location_name_search
