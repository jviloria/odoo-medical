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
from openerp.tools.translate import _

class MedicalPatientRecord(models.Model):
    '''
    Patient Medical Record.
    '''
    _name = 'medical.patient.record'
    _order = 'id desc'
    _rec_name = 'code'

    @api.one
    @api.constrains('code')
    def _check_unique_code(self):
        if len(self.search([('code', '=', self.code)])) > 1:
            raise ValidationError(_("Medical Record already exists and violates unique field constraint"))

    @api.model
    def create(self, vals):
        vals['is_created'] = True
        new_obj = super(MedicalPatientRecord, self).create(vals)
        patient = self.env['medical.patient'].browse(vals['patient_id'])
        patient.emr_id = new_obj.id
        return new_obj

    code = fields.Char(related='patient_id.ref',
        string='Record Number', store=True)
    patient_name = fields.Char(related='patient_id.name',
    	string ='Patient Name')
    evaluation_ids = fields.One2many(comodel_name='medical.patient.evaluation', 
    	inverse_name='emr_id',
        string='Evaluations')
    patient_id = fields.Many2one('medical.patient', 
        string='Patient', required=True)
    date = fields.Datetime(string='Create Date',
    	default=lambda self: fields.Datetime.now())
    is_created = fields.Boolean('Created', default=False)
