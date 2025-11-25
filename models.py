
from app import db
from datetime import datetime


class user(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    # connection esta. between department and user table
    department_id = db.Column(db.Integer, db.ForeignKey('departments.db'), nullable=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(50), nullable=False)      # e.g. 'doctor', patients,'admin'
    Created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Reverse relationship
    department = db.relationship("Department", back_populate="doctors")

class patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10))
    contect = db.Column(db.String(15))
    address = db.Column(db.text)


class Doctor(db.Model):
    __tablename__ = 'doctor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    contact = db.Column(db.String(15))



class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    department_name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.text, nullable=True)

    doctors = db.relationship("user", back_populates="department")
    



class Apponintment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(40))
    time = db.Column(db.String(40))
    status = db.Column(db.String(60), nullable=False, default="Booked") # booked, complted, cancle
    user_id = db.Column(db.Integer, db.ForeignKey('users.id') ) #patient id
    treatement_id = db.Column(db.Integer, db.ForeignKey('treatments.id'), unique=True,)            
    notes = db.Column(db.text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    #Relationships patients and doctor



class Treatment(db.Model):
    __tablename__='treatments'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    diagnosis = db.Column(db.text, nullable=False)
    prescription = db.Column(db.text)
    notes = db.Column(db.text)
    appointment = db.relationship("Apponintment", backref="treatments")


