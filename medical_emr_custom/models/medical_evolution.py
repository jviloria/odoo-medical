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
import time

class MedicalPatientEvolution(models.Model):
    '''
    Patient Disease Evolution.
    '''
    _name = 'medical.patient.evolution'
    _order = 'id desc'
    _rec_name = 'id'

    # @api.onchange('evaluation_id')
    # def onchange_evaluation_id(self):
    #     eva_id = self.env['medical.patient.evaluation'].search([('id','=',self.evaluation_id.id)])
    #     _logger.warning("*"*30)
    #     _logger.warning("EVAL ID: %s" % (eva_id, ))
    #     _logger.warning("*"*30)
    #     if not self.evaluation_id :
    #         self.patient_id = False
    #     else:
    #         #eva_id = self.env['medical.patient.evaluation'].search([('id','=',self.evaluation_id)])
    #         self.patient_id = self.evaluation_id.patient_id.id
    #     return {}

    def onchange_evaluation_id(self, cr, uid, ids, evaluation_id=None, context=None):
        patient_id = False
        if evaluation_id:
            try:
                patient_id = self.pool.get('medical.patient.evaluation').browse(cr, uid, evaluation_id)[0].patient_id.id
            except:
                pass
        return {
                'value': { 'patient_id': patient_id,}
                }

    def create(self, cr, uid, vals, context=None):
        vals['is_created'] = True
        if 'evaluation_id' in vals:
            patient_id = self.pool.get('medical.patient.evaluation').\
                browse(cr, uid, [vals['evaluation_id']], context=context)[0].patient_id.id
            if patient_id:
                vals['patient_id'] = patient_id
        res = super(MedicalPatientEvolution, self).create(cr, uid, vals, context=context)
        return res

    def _doctor_id_get(self, cr, uid, context=None):
        partner_id = self.pool.get('res.users').browse(cr, uid, uid)[0].partner_id.id
        return self.pool.get('medical.physician').search(cr, uid, [('partner_id','=',partner_id)])[0] \
                if  self.pool.get('medical.physician').search(cr, uid, [('partner_id','=',partner_id)]) \
                else False

    name = fields.Char('Description',size=100)
    evaluation_id = fields.Many2one('medical.patient.evaluation', 
        string='Evaluation', required=True)
    patient_id = fields.Many2one('medical.patient', 
        string='Patient', readonly=True)
    date = fields.Datetime(string='Date')
    evolution_text = fields.Text(string='Evolution',
        help='Description of evolution.')
    is_created = fields.Boolean('Created')
    doctor_id = fields.Many2one('medical.physician', string='Doctor',
                                     readonly=True)  #required=True)

    _defaults = {
        'date': lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
        'is_created': False,
        'doctor_id': _doctor_id_get,
    }