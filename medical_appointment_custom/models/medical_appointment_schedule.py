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


class MedicalAppointmentSchedule(models.Model):
    _name = 'medical.appointment.schedule.time'
    #_order = 'physician_id,physician_schedule_id, patient_turn'

    name = fields.Char('Name')
    hours = fields.Char('Hours')
    minutes = fields.Char('Minutes')
    date = fields.Date('Date')
    appointment_date = fields.Datetime('Appointment Date')
    is_free = fields.Boolean('Is Free?', default=True)
    physician_schedule_id = fields.Many2one('medical.physician.schedule.template', 
    		string='Physician Schedule')