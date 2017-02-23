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
from datetime import datetime
from datetime import timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF, DEFAULT_SERVER_DATETIME_FORMAT as DTF
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
import pytz
import logging


_logger = logging.getLogger(__name__)

hours = [
    ('6', '6 AM'),
    ('7', '7 AM'),
    ('8', '8 AM'),
    ('9', '9 AM'),
    ('10', '10 AM'),
    ('11', '11 AM'),
    ('12', '12 M'),
    ('13', '1 PM'),
    ('14', '2 PM'),
    ('15', '3 PM'),
    ('16', '4 PM'),
    ('17', '5 PM'),
    ('18', '6 PM'),
    ('19', '7 PM'),
    ('20', '8 PM'),
]

def date_to_local(dt):    #Recibe objeto datetime sin timezone o UTC
    local_tz = pytz.timezone("America/Bogota")
    try:    #Se trata de ubicar la fecha en horario UTC
        dt = dt.replace(tzinfo=None) #Por si llega con timezone
        utc_tz = pytz.utc
        dt = utc_tz.localize(dt)
    except:
        _logger.critical("ERROR EN DATE TO LOCAL")
    
    return dt.astimezone(local_tz)

def date_to_utc(dt):    #Recibe objeto datetime sin timezone
    tz = pytz.timezone("America/Bogota")
    dt = tz.localize(dt)
    return dt.astimezone(pytz.utc)

def str_to_datetime(strdate):
    try:
        return datetime.strptime(strdate, DF)
    except:
        return datetime.strptime(strdate, DTF)

def spanish_string_date(date, appointment_date=None): #appointment_date es datetime UTC
    days = [('monday','Lunes'),('tuesday','Martes'),('wednesday','Miercoles'),
            ('thursday','Jueves'),('friday','Viernes'),('saturday','Sabado'),
            ('sunday','Domingo'),]
    months = [('january','Enero'),('february','Febrero'),('march','Marzo'),
            ('april','Abril'),('may','Mayo'),('june','Junio'),('july','Julio'),
            ('august','Agosto'),('september','Septiembre'),('october','Octubre'),
            ('november','Noviembre'),('december','Diciembre')]
    dt = str_to_datetime(date) 
    day_name = [x[1] for x in days if x[0] == dt.strftime("%A").lower()][0]
    month_name = [x[1] for x in months if x[0] == dt.strftime("%B").lower()][0]
    #Se incluye la hora en la fecha
    hour = date_to_local(appointment_date).strftime("%I:%M %p") if \
        appointment_date else ''

    return "%s %s de %s %s" % (day_name, dt.strftime("%d"), month_name, hour)

def utc_datetime_assembly(date, str_hour, str_min):
    '''
    Parámetros:
        date: String tipo date
        str_hour: String representando la hora ej: 07
        str_min: String representando los minutos ej: 15
    Retorna: 
        Objeto Datetime con timezone (UTC)
    '''
    try:
        appointment_hour = "timedelta(hours=%s) + timedelta(minutes=%s)" % \
                (str_hour, str_min)
        datetime_utc = date_to_utc( datetime.combine(str_to_datetime(date), \
                datetime.min.time()) + eval(appointment_hour) )
    except:
        return False
    return datetime_utc

class MedicalPhysicianScheduleTemplate(models.Model):
    _inherit = 'medical.physician.schedule.template'
    _order = 'date'

    def _status_search_fnc(self, operator, value):
        today = datetime.today().date()
        ids = []
        schedules = self.env['medical.physician.schedule.template'].search([('active','=', True)])
        if value == 'overdue':
            for schedule in schedules:
                if str_to_datetime(schedule.date).date() < today:
                    ids.append(schedule.id)
        if value == 'full':
            for schedule in schedules:
                if schedule.available_quota <= 0:
                    ids.append(schedule.id)

        return [('id','in',ids)]

    @api.model
    def _deactivate_overdue(self):
        for record in self.env['medical.physician.schedule.template'].search([('status','=','overdue')]):
            record.active = False

    @api.model
    def create(self, vals):
        if 'date' in vals:
            try:
                physician_name = self.env['medical.physician'].search([('id','=',vals['physician_id'])])[0].name
                vals['name'] = "%s Dr %s" % (spanish_string_date(vals['date']), physician_name)
            except:
                pass
        for appointment in self.appointment_ids:
            appointment.physician_id = vals['physician_id']
        return super(MedicalPhysicianScheduleTemplate, self).create(vals)

    def _time_schedule_disable(self, appointment_obj):
        #_logger.critical("STAGE NAME: %s" % appointment_obj.stage_name)
        if appointment_obj.stage_name in ['Canceled','canceled','Cancelado']:
            appointment_obj.time_schedule_id.is_free = True
        else:
            appointment_obj.time_schedule_id.is_free = False

    @api.multi
    def write(self, vals):
        res = super(MedicalPhysicianScheduleTemplate, self).write(vals)
        for appointment in self.appointment_ids:
            self._time_schedule_disable(appointment)
            #Se cambió el nombre del médico, se reasignan las citas
            if 'physician_id' in vals:
                appointment.physician_id = self.physician_id
            if 'date' in vals:  #Se cambió la fecha
                dt1 = str_to_datetime(vals['date']).date()
                dt2 = str_to_datetime(appointment.time_schedule_id.appointment_date).date()
                diff = dt1 - dt2
                new_date = str_to_datetime(appointment.time_schedule_id.appointment_date) + diff
                appointment.time_schedule_id.appointment_date = new_date
                appointment.appointment_date = new_date
        if 'date' in vals:
            self.name = "%s Dr %s" % (spanish_string_date(self.date), self.physician_id.name)

        return res

    @api.multi
    #@api.onchange('specialty_id')
    def onchange_date(self, date, start_hour, end_hour=None,start_minute=None,end_minute=None):
        if not date or not start_hour or not end_hour:
            return False
        start_minute = 'timedelta(minutes=%s)' % start_minute if start_minute else 'timedelta(minutes=0)'
        end_minute = 'timedelta(minutes=%s)' % end_minute if end_minute else 'timedelta(minutes=0)'
        start_hour = 'timedelta(hours=%s)' % start_hour if start_hour else 'timedelta(hours=0)'
        end_hour = 'timedelta(hours=%s)' % end_hour if end_hour else 'timedelta(hours=0)'
        try:
            appointment_date = str_to_datetime(date) + eval(start_hour) + eval(start_minute)
            date_string = spanish_string_date(date, date_to_utc(appointment_date))
        except:
            _logger.critical("ERROR EN SPANISH STRING DATE")
            date_string = False

        date = str_to_datetime(date)
        appointment_date = date + eval(start_hour) + eval(start_minute)
        appointment_date = date_to_utc(appointment_date)
        appointment_date_end = False
        if end_hour:
            appointment_date_end = date + eval(end_hour) + eval(end_minute)
            appointment_date_end = date_to_utc(appointment_date_end)

        return {
            'value':{
            'date_string': date_string,
            'appointment_date': appointment_date,
            'appointment_date_end': appointment_date_end,
            }
        }

    @api.depends('available_quota','date')
    def _set_status(self):
        today = datetime.today().date()
        for record in self:
            try:
                if str_to_datetime(record.date).date() < today:
                    record.status = 'overdue'
                elif record.available_quota <= 0:
                    record.status = 'full'
                else:
                    record.status = 'valid'
            except:
                pass

    @api.depends('appointment_quota', 'scheduled_appointments')
    def _available_quota(self):
        for record in self:
            record.available_quota = record.appointment_quota - record.scheduled_appointments

    @api.depends('appointment_ids')
    def _appointment_count(self):
        for record in self:
            appointments = self.env['medical.appointment'].search([\
                    ('physician_schedule_id','=',record.id), \
                    ('stage_name','not in',['canceled','Canceled','Cancelado'])])
            record.scheduled_appointments = len(appointments)

    @api.multi
    #@api.onchange('specialty_id')
    def onchange_specialty_id(self, specialty_id):
        res = {}
        doctors = self.env['medical.physician'].search([('specialty_id','=', specialty_id)])
        ids = [doctor.id for doctor in doctors]
        res['domain'] = {'physician_id': [('id','in',ids)]}
        return res

    def _increase_quota(self, date_start):
        time_schedule_obj = self.env['medical.appointment.schedule.time']
        records = time_schedule_obj.search([('physician_schedule_id','=', self.id)])
        step = eval('timedelta(minutes=%s)' % self.step)
        for x in range(0,self.appointment_quota):
            #res = [x for x in records if x.appointment_date == date_start]
            res = []
            for x in records:
                appointment_date = str_to_datetime(x.appointment_date)
                if appointment_date == date_start:
                    res.append(appointment_date)
            if not res:
                vals={
                    'appointment_date': date_start,
                    'physician_schedule_id': self.id,
                    'name': date_to_local(date_start).strftime("%I:%M %p"),
                }
                time_schedule_obj.create(vals)
            date_start += step
        return True

    @api.one
    def create_appointment_schedule(self):
        time_schedule_obj = self.env['medical.appointment.schedule.time']
        res = time_schedule_obj.search([('physician_schedule_id','=', self.id)])
        if res and len(res) >= self.appointment_quota:
            raise ValidationError(_("Agenda ya ha sido generada previamente..."))
        try:
            date_start = str_to_datetime(self.appointment_date)
            date_end = str_to_datetime(self.appointment_date_end)
        except:
            raise ValidationError(_("Fecha no valida..."))
        if date_start >= date_end:   #Fechas no válidas
            raise ValidationError(_("Fecha de inicio mayor o igual que la fecha final..."))
        if res and self.appointment_quota > len(res):   #Se desea aumentar el cupo
            return self._increase_quota(date_start)
        step = timedelta(minutes=10)
        while date_start < date_end:
            vals={
                'appointment_date': date_start,
                'physician_schedule_id': self.id,
                'name': date_to_local(date_start).strftime("%I:%M %p"),
            }
            time_schedule_obj.create(vals)
            date_start += step
        _logger.critical("HORARIO CREADO...")
        quota = len(time_schedule_obj.search([('physician_schedule_id','=', self.id)]))
        self.appointment_quota = quota #if quota > self.appointment_quota else self.appointment_quota
        return True

    name = fields.Char('Name', default='New')
    specialty_id = fields.Many2one(
        'medical.specialty', string='Specialty', required=True,
        help='Specialty Code')
    status = fields.Char(compute='_set_status', string=_('Status'), 
        default='valid', search='_status_search_fnc')
    date_string = fields.Char(string='Date String')
    date = fields.Date('Date', required=True)
    appointment_quota = fields.Integer('Appointment Quota', default=10)
    is_over_quota = fields.Boolean('Is Over Quota', default=False)
    scheduled_appointments = fields.Integer(compute='_appointment_count', string=_('Scheduled Appointments'))
    available_quota = fields.Integer(compute='_available_quota', string=_('Quota Available'))
    appointment_ids = fields.One2many(comodel_name='medical.appointment',
        inverse_name='physician_schedule_id',
        string='Apointments', domain=[('stage_name','not in',['Done','done'])])
    active = fields.Boolean('Active', default=True)
    appointment_date = fields.Datetime('Next Appointment Date')
    appointment_date_end = fields.Datetime('End Appointment Date')
    start_hour = fields.Selection(hours, string='Start Hour')
    end_hour = fields.Selection(hours, string='End Hour')
    step = fields.Integer('Appointment Interval', default=10)
