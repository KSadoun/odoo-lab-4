from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
import re

class HmsPatient(models.Model):
    _name = 'hms.patient'
    _description = 'Hospital Patient'

    first_name = fields.Char(string='First Name', required=True)
    last_name = fields.Char(string='Last Name', required=True)
    email = fields.Char(string='Email', required=True)
    
    age = fields.Integer(
        string='Age', 
        compute='_compute_age', 
        store=True, 
        readonly=True 
    )
    
    birth_date = fields.Date(string='Birth Date', required=True)
    
    blood_type = fields.Selection([
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ], string='Blood Type')
    
    pcr = fields.Boolean(string='PCR Checked')
    cr_ratio = fields.Float(string='CR Ratio')
    history = fields.Text(string='Medical History')
    address = fields.Text(string='Address')
    image = fields.Binary(string='Patient Image')

    state = fields.Selection([
        ('Undetermined', 'Undetermined'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
        ('Serious', 'Serious')
    ], string='Status', default='Undetermined', required=True)

    department_id = fields.Many2one('hms.department', string='Department')
    doctor_ids = fields.Many2many('hms.doctor', string='Doctors')
    log_ids = fields.One2many('hms.patient.log', 'patient_id', string='History Logs')

    department_capacity = fields.Integer(
        related='department_id.capacity', 
        string='Department Capacity', 
        readonly=True
    )

    def action_set_good(self):
        for record in self:
            record.state = 'Good'

    def action_set_fair(self):
        for record in self:
            record.state = 'Fair'

    def action_set_serious(self):
        for record in self:
            record.state = 'Serious'

    _sql_constraints = [
        ('unique_email', 'UNIQUE(email)', 'The email address must be unique!')
    ]

    @api.depends('birth_date')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.birth_date:
                birth_date = record.birth_date
                age = today.year - birth_date.year
                if today.month < birth_date.month or \
                   (today.month == birth_date.month and today.day < birth_date.day):
                    age -= 1
                record.age = age
            else:
                record.age = 0

    @api.constrains('email')
    def _check_email(self):
        for record in self:
            if record.email:
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, record.email):
                    raise ValidationError(_("Invalid email format! Please enter a valid email address."))

    @api.constrains('pcr', 'cr_ratio')
    def _check_pcr_ratio(self):
        for record in self:
            if record.pcr and not record.cr_ratio:
                raise ValidationError(_("CR Ratio is mandatory if PCR is checked."))

    @api.onchange('birth_date')
    def _onchange_birth_date(self):
        if self.birth_date:
            today = date.today()
            age = today.year - self.birth_date.year
            if today.month < self.birth_date.month or \
               (today.month == self.birth_date.month and today.day < self.birth_date.day):
                age -= 1
            
            # Auto update matching field during interface modification
            self.age = age

    @api.onchange('age')
    def _onchange_age(self):
        if self.age and self.age < 30:
            self.pcr = True
            return {
                'warning': {
                    'title': "PCR Checked Automatically",
                    'message': "The PCR field has been checked because the patient's age is under 30.",
                    'type': 'notification'
                }
            }

    @api.model_create_multi
    def create(self, vals_list):
        records = super(HmsPatient, self).create(vals_list)
        for record in records:
            self.env['hms.patient.log'].create({
                'patient_id': record.id,
                'description': f"State changed to {record.state}"
            })
        return records

    def write(self, vals):
        if 'state' in vals:
            for record in self:
                if record._origin.state != vals['state']:
                    self.env['hms.patient.log'].create({
                        'patient_id': record.id,
                        'description': f"State changed to {vals['state']}"
                    })
        return super(HmsPatient, self).write(vals)