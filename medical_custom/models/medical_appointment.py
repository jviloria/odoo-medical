# -*- coding: utf-8 -*-
# #############################################################################
#
# John W. Viloria Amaris
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# #############################################################################

from openerp import models, fields, api
import time

class MedicalAppointment(models.Model):
    _inherit = 'medical.appointment'

    @api.model
    def create(self, vals):
        res = super(MedicalAppointment, self).create(vals)
        self._eapb_order_set(res)
        last_evaluation_id = self._last_evaluation_get(res)
        res.evaluation_id = last_evaluation_id.id if last_evaluation_id else False
        return res

    @api.multi
    def write(self, vals):
        vals['date_end'] = False
        vals['duration'] = 0.16666666666666666
        res = super(MedicalAppointment, self).write(vals)
        last_evaluation_id = self._last_evaluation_get(self.search([('id','=',self.id)]))
        vals['evaluation_id'] = last_evaluation_id.id if last_evaluation_id else False
        res = super(MedicalAppointment, self).write(vals)
        self._eapb_order_set(self.search([('id','in',self.ids)]))
        return res

    def _eapb_order_set(self, appointments):
        for appointment in appointments:
            if appointment.eapb_order_id:
                appointment.eapb_order_id.patient_id = appointment.patient_id.id
        return True

    def _last_evaluation_get(self, appointment):
        #Se localiza la última cita del paciente
        evaluation = self.env['medical.patient.evaluation'].search(
            [('patient_id','=',appointment.patient_id.id)], 
            order='id DESC', limit=1)
        if evaluation:
            return evaluation[0]
        return False


    duration = fields.Float('Duration', _default=10.00)
    evaluation_id = fields.Many2one('medical.patient.evaluation', 
        string="Patient Evaluation", _default=False)
    eapb_order_id = fields.Many2one('medical.eapb.order', 
        string="EAPB Order")
    evaluation_type_id = fields.Many2one('medical.evaluation.type', 
        string="Evaluation Type")
    eapb_id = fields.Many2one(related='patient_id.eapb_id', 
        string='EAPB', readonly=True,
        required=True)
    specialty_id = fields.Many2one(related='physician_id.specialty_id',
        string='Specialty', readonly=True,
        help='Medical Specialty / Sector')
    emr_id = fields.Many2one(related='patient_id.emr_id', 
        string="Patient Medical Record")