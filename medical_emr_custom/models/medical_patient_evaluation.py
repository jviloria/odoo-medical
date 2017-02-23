# -*- coding: utf-8 -*-
###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.techreceptives.com>)
#    Special Credit and Thanks to Thymbra Latinoamericana S.A.
#    Ported to 8.0 by Dave Lasley - LasLabs (https://laslabs.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
import time
from openerp import SUPERUSER_ID

class MedicalPatientEvaluation(orm.Model):
    _inherit = 'medical.patient.evaluation'
    _order = 'id desc'
    _rec_name = 'id'

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        args = args[:]
        ids = []
        if name:
            ids = self.search(cr, uid,
                              [('id', '=', name )] + args,
                              limit=limit)
        else:
            ids = self.search(cr, uid, args, context=context, limit=limit)
        return self.name_get(cr, uid, ids, context=context)

    def name_get(self, cr, uid, ids, context=None):
        res = []
        evaluations = self.browse(cr, uid, ids, context)
        for evaluation in evaluations:
            patient_name = ''
            if evaluation.patient_name:
                patient_name = evaluation.patient_name
            display_name = "%s" % (evaluation.id)
            res.append((evaluation.id, display_name))
        return res

    def _specialty_id_get(self, cr, uid, doctor_id, context=None):
        return self.pool.get('medical.physician').browse(cr, uid, doctor_id)[0].specialty_id.id

    def _doctor_id_get(self, cr, uid, context=None):
        partner_id = self.pool.get('res.users').browse(cr, uid, uid)[0].partner_id.id
        return self.pool.get('medical.physician').search(cr, uid, [('partner_id','=',partner_id)])[0] \
                if  self.pool.get('medical.physician').search(cr, uid, [('partner_id','=',partner_id)]) \
                else False

    def onchange_doctor_id(self, cr, uid, ids, doctor_id, context=None):
        specialty_id = self.pool.get('medical.physician').browse(cr, uid, doctor_id)[0].specialty_id
        specialty_code = self.pool.get('medical.physician').browse(cr, uid, doctor_id)[0].specialty_id.code
        return {
                'value': { 'specialty_id': specialty_id,
                'specialty_code': specialty_code}
                }

    def _calculate_bmi(self, cr, uid, height, weight, context=None):
        bmi = 0
        if weight > 0 and height > 0:
            bmi = weight / (height * height)
        return bmi

    def onchange_height_weight(self, cr, uid, ids, height, weight, context=None):
        bmi = self._calculate_bmi(cr, uid, height, weight)
        return {
                'value': { 'bmi': bmi,}
                }

    def create(self, cr, uid, vals, context=None):
        vals['is_created'] = True
        vals['evaluation_endtime'] = time.strftime("%Y-%m-%d %H:%M:%S")
        patient_id = vals['patient_id']
        emr_id = self.pool.get('medical.patient').browse(cr, uid, [patient_id])[0].emr_id.id
        if not emr_id:
            emr_id = self.pool.get('medical.patient.record').search(cr, uid, [('patient_id','=',patient_id)])[0]
            if not emr_id:
                emr_id = self.pool.get('medical.patient.record').create(cr, SUPERUSER_ID, {'patient_id': patient_id}, context=context)
            else:
                self.pool.get('medical.patient').write(cr, uid, [patient_id],{'emr_id': emr_id}, context=context)
        vals['emr_id'] = emr_id
        if 'height' in vals and 'weight' in vals:
            if vals['height'] > 0 and vals['weight'] > 0:
                vals['bmi'] = self._calculate_bmi(cr, uid, vals['height'], vals['weight'])
        res = super(MedicalPatientEvaluation, self).create(cr, uid, vals, context=context)
        doctor_id = self.browse(cr, uid, res, context=context)[0].doctor_id.id
        specialty_id = self._specialty_id_get(cr, uid, doctor_id, context=context)
        super(MedicalPatientEvaluation, self).write(cr, uid, res, {'specialty_id': specialty_id}, context=context)
        return res

    _columns = {
        'evaluation_date': fields.date(
            string='Evaluation Date',
            required=True
        ),
        'blood_pressure': fields.char(
            size=20, string='Blood Pressure',
            help="Patient Blood Pressure"
        ),
        'cockcroft_gault': fields.char(
            string='Cockcroft - Gault'),
        'mdrd': fields.char(
            string='MDRD'),
        'head_neck': fields.char(
            string='Head and Neck'),
        'chest': fields.char(
            string='Chest'),
        'abdomen': fields.char(
            string='Abdomen'),
        'extremities': fields.char(
            string='Extremities'),
        'neurological': fields.char(
            string='Neurological'),
        'genitals': fields.char(
            string='Genitals and urinary'),
        'cardiopulmonary': fields.char(
            string='Cardiopulmonary'),
        'others': fields.char(
            string='Others'),
        'ekg': fields.text(
            string='EKG Test Result'),
        'vldl': fields.char(
            string='Last VLDL',
            help='Last VLDL Cholesterol reading. Can be approximative'),
        'triglycerides': fields.char(
            string='Last Triglycerides',
            help='Last Triglycerides reading. Can be approximative'),
        'cbc_test': fields.text(
            string='CBC Test Result'),
        'other_test': fields.text(
            string='Other Test Result'),
        'dx1': fields.many2one('medical.pathology',
            string='DX1', required=True),
        'dx2': fields.many2one('medical.pathology',
            string='DX2'),
        'dx3': fields.many2one('medical.pathology',
            string='DX3'),
        'dx4': fields.many2one('medical.pathology',
            string='DX4'),
        'referred': fields.text(
            string='Referred to...'),
        'doctor_id': fields.many2one('medical.physician', string='Doctor',
                                     readonly=False,
                                     required=True),
        'patient_name': fields.related('patient_id', 'name', string='Patient Name', type='char', store=False, readonly=True),
        'evaluation_type': fields.many2one('medical.evaluation.type',
            string='Type'),
        #'bpm': fields.char(string='Heart Rate',
        #                      help='Heart rate expressed in beats per minute'),
        #'respiratory_rate': fields.char(
        #    string='Respiratory Rate',
        #    help='Respiratory rate expressed in breaths per minute'),
        #'temperature': fields.char(string='Temperature',
        #                            help='Temperature in celcius'),
        #'weight': fields.char(string='Weight',
        #                       help='Weight in Kilos'),
        'height': fields.float(string='Height',
                               help='Height in meters, eg 1,75'),
        #'bmi': fields.char(string='Body Mass Index'),
        'glycemia': fields.char(
            string='Glycemia',
            help='Last blood glucose level. Can be approximative.'
        ),
        'cholesterol_total': fields.char(string='Last Cholesterol'),
        'hdl': fields.char(string='Last HDL'),
        'ldl': fields.char(
            string='Last LDL',
            help='Last LDL Cholesterol reading. Can be approximative'
        ),
        'imagenologic': fields.text(
            string='Imagenologic Report'),
        'evolution_ids': fields.one2many('medical.patient.evolution', 'evaluation_id', string='Patient Evolutions'),
        'is_created':fields.boolean('Created'),
        'directions': fields.text(string='Plan', required=True),
        'present_illness': fields.text(string='Present Illness', required=True),
        'breasts': fields.char(
            string='Breasts'),
        'specialty_code': fields.char('Specialty Code'),
        'uterine_tone': fields.char('Uterine Tone'),
        'uterine_activity': fields.char('Uterine Activity'),
        'fetal_presentation': fields.char('fetal presentation'),
        'fetal_situation': fields.char('Fetal Situation'),
        'fetal_fcf': fields.char('FCF'),
        'fetal_moves': fields.char('Fetal Moves'),
        'evaluation_endtime': fields.datetime(string='End', required=False),
        'emr_id': fields.many2one('medical.patient.record',
            string='Medical Record ID'),
        'eapb_order_id': fields.many2one('medical.appointment',
            string='EAPB Order ID'),
    }

    _defaults = {
        'is_created': False,
        'doctor_id': _doctor_id_get,
        'evaluation_date': lambda *a: time.strftime("%Y-%m-%d"),
        'evaluation_start': lambda *a: time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
class MedicalEvaluationType(orm.Model):

    _name = 'medical.evaluation.type'

    _columns = {
        'name': fields.char(
            string='Description',
        ),
        'code': fields.char(
            size=6, string='Code'),

    }    