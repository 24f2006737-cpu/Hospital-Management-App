from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)  # Flask app banate  hain 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECERET_KEY"] = "YOUR_SECERET_KEY_2025"  # for session management(session ke liye juoori ha)

db = SQLAlchemy(app)


###------------- Models -------------###
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)      # e.g. 'doctor', patients,'admin'
    Created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):      # __repr__ debugging ke liye use hota hai
        return f"<User {self.username}>"
    
    
# patient model
class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(5))
    contact = db.Column(db.String(15))
    address = db.Column(db.Text)

    def __repr__(self):
        return f"<Patient {self.name}>"


# Doctor model
class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100))
    contact = db.Column(db.String(15))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    
    def __repr__(self): 
        return f"<Doctor {self.name}>"


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationship one department can have many doctors 
    doctors = db.relationship("Doctor", backref="department", lazy=True)

    @property   # property kitne doctors registered hain is department me
    def doctors_registered(self):
        return len(self.doctors)
    def __repr__(self):
        return f"<Department {self.name}>"
    


#Appointment model
class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)  #Foreignkey
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Booked") # booked, complted, cancle    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('Patient', backref='appointments')  #Relationship
    doctor = db.relationship('Doctor', backref='appointments')

    def __repr__(self):
        return f"<Appointment {self.id} - {self.status}>"
    
    


# Treatment model
class Treatment(db.Model):
    __tablename__='treatments'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text)
    notes = db.Column(db.Text)
    appointment = db.relationship("Appointment", backref="treatments")
    
    def __repr__(self):
        return f"<Treatment {self.id}>"


#------------------------ Routes ------------------------#
@app.route('/')
def home():
    return "Hospital Management System"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("\n" + "="*50)
        print("Table created successfully! ")
        print("="*50)

    # print table name  
        print("\n" "Tables in Database")
        for i, table in enumerate(db.metadata.tables.keys(), 1):
            print(f" {i}. {table}")
    

# create default admin 
        admin = User.query.filter_by(username="admin").first()

        if not admin:
            admin = User(
                username ='admin',
                email = 'adminhospital@gmail.com',
                password=generate_password_hash('admin123'),
                role = 'admin'
            )

            db.session.add(admin)
            db.session.commit()

        print("\n" + "="*50 + "\n")
    app.run(debug=True)
