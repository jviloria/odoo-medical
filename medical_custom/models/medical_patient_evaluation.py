# -*- coding: utf-8 -*-
###############################################################################
#
#    John W. Viloria Amaris
#
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

from openerp import fields, models
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import logging

_logger = logging.getLogger(__name__)

class MedicalPatientEvaluation(models.Model):
    _inherit = 'medical.patient.evaluation'

    def create(self, cr, uid, vals, context=None):
        res = super(MedicalPatientEvaluation, self).create(cr, uid, vals, context=context)
        vals = {}
        appointment_ids = self.browse(cr, uid, [res], context=context)[0].patient_id.appointment_ids
        if appointment_ids:
            _logger.warning("*"*30)
            today = datetime.now().date()
            _logger.warning("TODAY: %s" % today)
            for appointment in appointment_ids:
                appointment_date = datetime.strptime(appointment.appointment_date, DTF).date()
                if today == appointment_date:   #SE ENCUENTRA UNA CITA PARA LA EVALUACION ACTUAL
                    _logger.warning("UNA FECHA ENCONTRADA: %s" % appointment_date)
                    #Se trae el numero de autorizacion desde la cita medica
                    vals['eapb_order_id'] = appointment.eapb_order_id.id if appointment.eapb_order_id else False
                    done_id = self.pool.get('medical.appointment.stage').search(cr, uid, [('name','in',['done','Done'])])
                    if done_id: #Se cambia el stage de la cita a 'Done'
                        self.pool.get('medical.appointment').write(cr, uid, [appointment.id], {'stage_id': done_id[0]}, context=context)
            _logger.warning("*"*30)
        super(MedicalPatientEvaluation, self).write(cr, uid, [res], vals, context=context)
        return res
