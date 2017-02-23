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
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

def str_to_datetime(strdate):
    try:
        return datetime.strptime(strdate, DF)
    except:
        return datetime.strptime(strdate, DTF)

class MedicalPatient(models.Model):
    '''
    The concept of Patient included in medical.
    '''
    _inherit = 'medical.patient'

    @api.multi
    def onchange_dob(self, dob=None):   #Se establece la medida de la edad
        age_type = '1'
        try:
            if str_to_datetime(dob):
                dob = str_to_datetime(dob).date()
                today = datetime.today().date()
                days =  (today - dob).days
                if (days / 365) > 0:    #Años
                    age_type = '1'
                elif (days / 30) > 0:   #Meses
                    age_type = '2'
                else:                   #Días
                    age_type = '3'
        except:
            pass

        return {
            'value':{
            'age_type': age_type,
            }
        }

    @api.multi
    def onchange_city_id(self, city_id):
        state_id = False
        city_obj = self.env['res.country.state.city'].search([('id','=',city_id)])
        if city_obj:
            state_id = city_obj.state_id.id

        return {
            'value':{
            'state_id': state_id,
            }
        }

    @api.model
    def _get_default_eapb(self):
        eapb = self.env['medical.eapb']._get_default()
        return eapb or False

    @api.model
    def _get_default_city(self):
        city = self.env['res.country.state.city']._get_default()
        return city or False

    @api.one
    @api.constrains('ref')
    def _check_unique_ref(self):
        if len(self.search([('ref', '=', self.ref)])) > 1:
            raise ValidationError(_("Patient already exists and violates unique field constraint"))

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('name', operator, name), ('ref', operator, name)]
        patient = self.search(domain + args, limit=limit)
        return patient.name_get()

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['is_patient'] = True
        if not vals.get('identification_code'):
            sequence = self.env['ir.sequence'].get('medical.patient')
            vals['identification_code'] = sequence
        if not 'name' in vals:
            try:
                vals['name'] = self._complete_name([vals.get('primary_last_name',False),
                    vals.get('second_last_name',False), vals.get('first_name',False),
                    vals.get('middle_name',False)])
            except:
                pass
        return super(MedicalPatient, self).create(vals)

    def write(self, cr, uid, ids, vals, context=None):
        if [x for x in ['primary_last_name', 'second_last_name', 'first_name', 'middle_name'] if x in vals]:
            res = super(MedicalPatient, self).write(cr, uid, ids, vals, context)
            for p in self.browse(cr, uid, ids, context=context):
                vals['name'] = self._complete_name([p.primary_last_name, p.second_last_name, p.first_name, p.middle_name])
        return super(MedicalPatient, self).write(cr, uid, ids, vals, context)

    def _complete_name(self, names):
        return ' '.join([name for name in names if name])


    @api.multi
    def onchange_first_name(self, primary_last_name, second_last_name, first_name, middle_name):
        first_name = first_name.upper() if first_name else ''
        res = {'first_name':first_name}
        #Se establece el género del paciente
        #buscando en la bd existente
        if first_name and len(first_name) > 0:
            patient = self.search([('first_name','=',first_name)], limit=1)
            if patient:
                res['gender'] = patient.gender
            elif first_name[-1] in ('A','a'):
                res['gender'] = 'F'
            else:
                res['gender'] = 'M'
        try:
            name = self._complete_name([primary_last_name, second_last_name, first_name, middle_name]).upper()
        except:
            name = False
        res['name'] = name

        return {'value': res}

    @api.multi
    def onchange_names(self, primary_last_name, second_last_name, first_name, middle_name):
        names =  zip(
                    ['primary_last_name', 'second_last_name', 'first_name', 'middle_name'],
                    [primary_last_name, second_last_name, first_name, middle_name])
        try:
            name = self._complete_name([primary_last_name, second_last_name, first_name, middle_name]).upper()
        except:
            name = False
        res = {'name': name}
        for key,value in names:
            try:
                res[key] = value.upper()
            except:
                pass

        return {'value': res}

    first_name = fields.Char(
        string='First Name',
        required=True,
        help='Primer Nombre.')
    middle_name = fields.Char(
        string='Middle Name',
        help='Segundo Nombre.')
    primary_last_name = fields.Char(
        string='Primary Last Name',
        required=True,
        help='Primer Apellido.')
    second_last_name = fields.Char(
        string='Second Last Name',
        required=True,
        help='Segundo Apellido.')
    ref_type = fields.Selection([('CC','CEDULA DE CIUDADANIA'),
        ('TI','TARJETA DE IDENTIDAD'),
        ('CE','CEDULA DE EXTRANJERIA'),
        ('RC','REGISTRO CIVIL'),
        ('PA','PASAPORTE'),
        ('AS','ADULTO SIN IDENTIFICACION'),
        ('MS','MENOR SIN IDENTIFICACION'),
        ('NU','NUMERO UNICO DE IDENTIFICACION'),
        ], string='Reference Type',required=True, default='CC')
    patient_type = fields.Selection([('1','CONTRIBUTIVO'),
        ('2','SUBSIDIADO'),
        ('3','VINCULADO'),
        ('4','PARTICULAR'),
        ('5','OTRO'),
        ], string='Patient Type',required=True, default='2')    
    age_type = fields.Selection([('1','ANIOS'),
        ('2','MESES'),
        ('3','DIAS'),
        ], string='Age Type',required=True, default='1')        
    residence_area = fields.Selection([('U','URBANA'),
        ('R','RURAL'),
        ], string='Patient Area of Residence',required=True, default='U')            
    gender = fields.Selection([('M','MASCULINO'),
        ('F','FEMENINO'),
        ], string='Gender', translate=True,required=True)
    city_id = fields.Many2one('res.country.state.city', 
        string='City',required=True, default=_get_default_city)
    medical_history_personal_id = fields.Many2many('medical.personal.tags', 
        id1='medical_personal_tags_id', id2='medical_history_personal_id',
        string='Personal History', select=True)
    medical_history_family_id = fields.Many2many('medical.family.tags', 
        id1='medical_family_tags_id', id2='medical_history_family_id',
        string='Family History', select=True)
    medical_history_surgical_id = fields.Many2many('medical.surgical.tags', 
        id1='medical_surgical_tags_id', id2='medical_history_surgical_id',
        string='Surgical History', select=True)
    medical_history_pathological_id = fields.Many2many('medical.pathological.tags', 
        id1='medical_pathological_tags_id', id2='medical_history_pathological_id',
        string='Pathological History', select=True)
    medical_history_pharmacological_id = fields.Many2many('medical.pharmacological.tags', 
        id1='medical_pharmacological_tags_id', id2='medical_history_pharmacological_id',
        string='Pharmacological History', select=True)
    medical_history_gynecological_id = fields.Many2many('medical.gynecological.tags', 
        id1='medical_gynecological_tags_id', id2='medical_history_gynecological_id',
        string='Gynecological History', select=True)
    eapb_id = fields.Many2one('medical.eapb', 
        string='EAPB',required=True, default=_get_default_eapb)
    accompanist_ids = fields.One2many(comodel_name='medical.accompanist', 
        inverse_name='patient_id', 
        string='Patient Accompanists')
    evolution_ids = fields.One2many(comodel_name='medical.patient.evolution', 
        inverse_name='patient_id', 
        string='Patient Evolution')
    appointment_ids = fields.One2many(comodel_name='medical.appointment',
        inverse_name='patient_id',
        string='Apointments')

class patientMedicalHistoryPersonal(models.Model):

    _description = 'Medical Personal History'
    _name = 'medical.personal.tags'
    _order = 'name'

    name = fields.Char('Tag Name', required=True, 
        size=64, translate=True)
    active =  fields.Boolean('Active', 
        help="The active field allows you to hide the category without removing it.")

    _defaults = {
        'active': 1,
    }

class patientMedicalHistoryFamily(models.Model):

    _description = 'Medical Family History'
    _name = 'medical.family.tags'
    _order = 'name'

    name = fields.Char('Tag Name', required=True, 
        size=64, translate=True)
    active =  fields.Boolean('Active', 
        help="The active field allows you to hide the category without removing it.")

    _defaults = {
        'active': 1,
    }

class patientMedicalHistorySurgical(models.Model):

    _description = 'Medical Surgical History'
    _name = 'medical.surgical.tags'
    _order = 'name'

    name = fields.Char('Tag Name', required=True, 
        size=64, translate=True)
    active =  fields.Boolean('Active', 
        help="The active field allows you to hide the category without removing it.")

    _defaults = {
        'active': 1,
    }

class patientMedicalHistoryPathology(models.Model):

    _description = 'Medical Pathological History'
    _name = 'medical.pathological.tags'
    _order = 'name'

    name = fields.Char('Tag Name', required=True, 
        size=64, translate=True)
    active =  fields.Boolean('Active', 
        help="The active field allows you to hide the category without removing it.")

    _defaults = {
        'active': 1,
    }

class patientMedicalHistoryPharmacological(models.Model):

    _description = 'Medical Pharmacological History'
    _name = 'medical.pharmacological.tags'
    _order = 'name'

    name = fields.Char('Tag Name', required=True, 
        size=64, translate=True)
    active =  fields.Boolean('Active', 
        help="The active field allows you to hide the category without removing it.")

    _defaults = {
        'active': 1,
    }

class patientMedicalHistoryGynecological(models.Model):

    _description = 'Medical Gynecological History'
    _name = 'medical.gynecological.tags'
    _order = 'name'

    name = fields.Char('Tag Name', required=True, 
        size=64, translate=True)
    active =  fields.Boolean('Active', 
        help="The active field allows you to hide the category without removing it.")

    _defaults = {
        'active': 1,
    }

class patientMedicalEAPB(models.Model):

    _description = 'Patient EAPB'
    _name = 'medical.eapb'
    _order = 'name'

    @api.model
    def _get_default(self):
        #TODO:Configuración del code por defecto
        eapb = self.search([('name','ilike','COMFA')], limit=1)    #COMFACOR
        return eapb or False

    name = fields.Char('Name', required=True, 
        translate=True)
    code = fields.Char('EAPB Code', required=True, 
        translate=True)
    active =  fields.Boolean('Active', 
        help="The active field allows you to hide the category without removing it.")

    _defaults = {
        'active': 1,
    }
