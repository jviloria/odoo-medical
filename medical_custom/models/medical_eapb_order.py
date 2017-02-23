# -*- coding: utf-8 -*-
# #############################################################################
#
# John Winston Viloria Amaris.
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
from openerp.exceptions import ValidationError

class MedicalEapbOrder(models.Model):
    '''
    Medical Orders management.
    '''
    _name = 'medical.eapb.order'
    _order = 'id desc'
    _rec_name = 'code'

    @api.one
    @api.constrains('code','eapb_id')
    def _check_unique_code(self):
        domain = [
            ('code', '=', self.code),
            ('eapb_id', '=', self.eapb_id.id)
        ]
        if len(self.search(domain)) > 1:
            raise ValidationError('Medical Order already exists and violates unique field constraint')

    code = fields.Char('Order Number',required=True)
    patient_name = fields.Char(related='patient_id.name',
    	string ='Patient Name')
    evaluation_id = fields.Many2one('medical.patient.evaluation', string='Evaluation')
    patient_id = fields.Many2one('medical.patient', 
        string='Patient')
    date = fields.Datetime(string='Create Date',
    	default=lambda self: fields.Datetime.now())
    evaluation_date = fields.Datetime(related='evaluation_id.evaluation_start',
        string='Evaluation Datetime')
    is_created = fields.Boolean('Created', default=False)
    eapb_id = fields.Many2one('medical.eapb', string='EAPB',
        required=True)