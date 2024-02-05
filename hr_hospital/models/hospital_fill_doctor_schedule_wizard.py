import datetime
from odoo import fields, models
# from odoo.exceptions import ValidationError


class HospitalScheduleHour(models.TransientModel):
    _name = 'hospital.schedule.hour'
    _description = 'hospital schedule hour'
    hour = fields.Selection(selection=[('6', '6'), ('7', '7'), ('8', '8'),
                                       ('9', '9'), ('10', '10'), ('11', '11'),
                                       ('12', '12'), ('13', '13'),
                                       ('14', '14'), ('15', '15'),
                                       ('16', '16'), ('17', '17'),
                                       ('18', '18'), ('19', '19'),
                                       ('20', '20'), ('21', '21'),])

    def name_get(self):
        return [(rec.id, f'{rec.hour}') for rec in self]


class HospitalScheduleDay(models.TransientModel):
    _name = 'hospital.schedule.day'
    _description = 'hospital schedule day'
    weekday = fields.Selection(selection=[('0', 'Monday'),
                                          ('1', 'Tuesday'),
                                          ('2', 'Wednesday'),
                                          ('3', 'Thursday'),
                                          ('4', 'Friday'),
                                          ('5', 'Saturday'),
                                          ('6', 'Sunday')])
    hour_ids = fields.Many2many(comodel_name='hospital.schedule.hour',
                                string='Hours')

    def name_get(self):
        return [(rec.id, f'{rec.weekday}') for rec in self]


class HospitalFillDoctorScheduleWizard(models.TransientModel):
    _name = 'hospital.fill.doctor.schedule.wizard'
    _description = 'Hospital fill out the doctor\'s schedule'

    doctor_id = fields.Many2one(comodel_name='hospital.doctor')
    weekday_type = fields.Selection(selection=[('even', 'Even'),
                                               ('odd', 'Odd'),
                                               ('all', 'All')],
                                    default='all')
    date_start = fields.Date()
    date_end = fields.Date()
    weekday_ids = fields.Many2many(comodel_name='hospital.schedule.day',
                                   string='Weekdays')

    def to_fill_doctor_schedule(self):
        # в suitable_days получаем все дни из заданного интервала дат,
        # из четных / нечетных (как выбрано) недель
        suitable_days = []
        for rec in self:
            end_date = rec.date_end + datetime.timedelta(days=1)
            date_interval = end_date - rec.date_start
            for i in range(date_interval.days):
                one_day = rec.date_start + datetime.timedelta(i)
                week_num = one_day.isocalendar()[1]
                if (rec.weekday_type == 'all' or
                        (rec.weekday_type == 'even' and week_num % 2 == 0) or
                        (rec.weekday_type == 'odd' and week_num % 2 != 0)):
                    suitable_days.append(one_day)

            for one_day in suitable_days:
                for weekdays in rec.weekday_ids:
                    if weekdays.weekday != str(one_day.weekday()):
                        continue
                    for hours in weekdays.hour_ids:
                        if self.env['hospital.doctor.schedule'].\
                                sudo().search_count(
                                [('doctor_id', '=', rec.doctor_id.id),
                                 ('date', '=', one_day),
                                 ('hour', '=', int(hours.hour))]) == 0:
                            # print(rec.doctor_id.name, ' ',
                            #       weekdays.weekday, ' ', hours.hour)

                            self.env['hospital.doctor.schedule'].\
                                sudo().create(
                                {'doctor_id': rec.doctor_id.id,
                                 'date': one_day,
                                 'hour': int(hours.hour)})
