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
from openerp import models, fields


class MedicalAccompanist(models.Model):
    '''
    Accompanying the patient.
    '''
    _name = 'medical.accompanist'

    accompanist_id = fields.Many2one('res.partner', 
        string='Patient Accompanist')
    date = fields.Date(string='Date', 
    	help='Accompanying the patient')
    patient_id = fields.Many2one('medical.patient', 
        string='Patient ID')
    mobile = fields.Char(related="accompanist_id.mobile", 
        store=True)
