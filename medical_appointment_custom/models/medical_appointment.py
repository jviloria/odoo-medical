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
from openerp.addons.medical.medical_constants import minutes
from datetime import datetime, timedelta
from medical_physician_schedule_template import str_to_datetime, date_to_utc,\
        hours, utc_datetime_assembly
import logging

_logger = logging.getLogger(__name__)


class MedicalAppointment(models.Model):
    _inherit = 'medical.appointment'
    _order = 'physician_id,physician_schedule_id, patient_turn'
    #_order = 'physician_id,physician_schedule_id, stage_id, patient_turn'

    def _stage_id_get(self, value_list):
        stage_obj = self.env['medical.appointment.stage'].search([\
            ('name','in',value_list)])
        return stage_obj and stage_obj.id or False

    @api.one
    def set_appointment_cancel(self):
        _logger.critical("CANCEL BUTTON RAISED")
        value_list = ('Canceled','canceled','Cancelado')
        res = self._stage_id_get(value_list)
        self.stage_id = res if res else self.stage_id.id
        #return {'type': 'ir.actions.act_window_close'}

    @api.one
    def set_appointment_done(self):
        _logger.critical("DONE BUTTON RAISED")
        value_list = ('Done','done','Realizado')
        res = self._stage_id_get(value_list)
        self.stage_id = res if res else self.stage_id.id
        #return {'type': 'ir.actions.act_window_close'}

    @api.one
    def set_patient_turn(self):
        appointments = self.env['medical.appointment'].search([
            ('physician_schedule_id','=',self.physician_schedule_id.id),
            ('patient_turn','<',100)])
        if appointments:
            self.patient_turn = max([x.patient_turn for x in appointments]) + 1
        else:
            self.patient_turn = 1
        stage_obj = self.env['medical.appointment.stage'].search([\
            ('name','in',['waiting','Waiting','En Espera','En espera'])])
        self.stage_id = stage_obj and stage_obj.id or self.stage_id.id

    @api.multi
    def onchange_physician_schedule_id(self, physician_schedule_id):
        #TODO: Solo filtra en los registros nuevos
        physician_schedule_id = self._context.get('default_physician_schedule_id',False)
        records = self.env['medical.appointment.schedule.time'].\
                search([('physician_schedule_id','=',physician_schedule_id),
                        ('is_free','=',True)])
        ids = [x.id for x in records]
        return {'domain': {'time_schedule_id':[('id','in', ids)]}}


    @api.multi
    def onchange_time_schedule_id(self, time_schedule_id):
        appointment_date = False
        schedule_time_obj = self.env['medical.appointment.schedule.time'].\
                search([('id','=',time_schedule_id)])
        if schedule_time_obj:
            appointment_date = schedule_time_obj.appointment_date

        return {
            'value':{
            'appointment_date': appointment_date,
            }
        }

    @api.multi
    def write(self, vals):
        res = super(MedicalAppointment, self).write(vals)
        return res

    physician_schedule_id = fields.Many2one('medical.physician.schedule.template')
    patient_turn = fields.Integer('Patient Turn', default=999)
    #date = fields.Date('Date')
    parent_date = fields.Date(related='physician_schedule_id.date',string='Parent Date')
    hours = fields.Selection(hours, 'Hours')
    minutes = fields.Selection(minutes,'Minutes')
    stage_name = fields.Char(related='stage_id.name', string='Stage Name')
    time_schedule_id = fields.Many2one('medical.appointment.schedule.time', \
            string='Time Schedule', required=True)