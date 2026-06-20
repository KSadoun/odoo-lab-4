from odoo import models, fields

class PatientLog(models.Model):
    _name = 'hms.patient.log'
    
    created_by = fields.Char()
    date = fields.Date()
    description = fields.Text()
    patient_id = fields.Many2one('hms.patient')