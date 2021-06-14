from datetime import datetime

from sqlalchemy.orm import backref
from his import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    national_id = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    mobile_number = db.Column(db.String, nullable=False)
    gender = db.Column(db.String(6), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(10), nullable=False, default='patient')

    # patient 0..* - 1 doctor
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    patients = db.relationship('User')

    # medical history
    medical_history = db.Column(db.Text, nullable=True)
    # salary
    salary = db.Column(db.Text, nullable=True)
    # patient scans
    scans = db.relationship('CTScan', backref='patient', lazy=True)

    def __repr__(self):
        return f"{self.role} ('{self.username}', '{self.email}', '{self.gender}', '{self.age}')"

class Appointment(db.Model):
    id =db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        doctor = User.query.get(self.doctor_id)
        patient = User.query.get(self.patient_id)
        return f"Appointment between doctor: {doctor.username} and patient {patient.username} at {self.datetime.isoformat()}"

class CTScan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_file = db.Column(db.String(20), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        patient = User.query.get(self.id)
        return f'Patient {patient.username} scan image {self.image_file}'


class ContactUs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile_number = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Message('{self.name}', '{self.email}', '{self.mobile_number}', '{self.subject}', '{self.message}')"
