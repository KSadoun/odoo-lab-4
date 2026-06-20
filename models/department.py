from odoo import models, fields

class Department(models.Model):
    _name = 'hms.department'
    _rec_name = 'name'

    name = fields.Char(required=True)
    capacity = fields.Integer()
    is_opened = fields.Boolean(default=True)
    
    patient_ids = fields.One2many(comodel_name='hms.patient', inverse_name='department_id', string='Patients')