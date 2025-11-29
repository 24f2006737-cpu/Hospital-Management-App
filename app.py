from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import timedelta


app = Flask(__name__)  # Flask app banate  hain 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "hospital-management-secret-key-2024" # for session management(session ke liye juoori ha)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)  # Session 24 hours

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
    

#---------------DECORATORS------------------#

# check if user logged han ya nhi 
def login_required(f):  
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f): # check if user is admin
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash("Admin access required to view this page. ", "danger ")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# check if user is doctor
def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'doctor':
            flash("Doctor access required to view this page. ", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# check if user is patient 
def patient_required(f):
    """check if user is patient"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'patient':
            flash("patient access required to view this page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# -------- PUblic Routes --------- #

@app.route('/')
def home():
    return "Hospital Management System"

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Agar user already logged in hai
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif role == 'patient':
            return redirect(url_for('patient_dashboard'))
    
    # POST request (form submit)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            # Clear any old session data
            session.clear()
            
            # Set new session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session.permanent = True  # Make session permanent
            
            flash(f'Welcome back, {user.username}!', 'success')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif user.role == 'patient':
                return redirect(url_for('patient_dashboard'))
            else:
                flash('Invalid role!', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Invalid username or password!', 'danger')
            return redirect(url_for('login'))
    
    # GET request (show form)
    return render_template('login.html')


###-------------------------- Register Route --------------------------###
@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration with role selection"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']  # Get selected role
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact']
        address = request.form.get('address', '')
        
        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        # Check if email exists
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        
        # Create user account
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role  # Use selected role
        )
        db.session.add(new_user)
        db.session.flush()
        
        # Create profile based on role
        if role == 'patient':
            new_patient = Patient(
                name=name,
                age=age,
                gender=gender,
                contact=contact,
                address=address
            )
            db.session.add(new_patient)
        
        elif role == 'doctor':
            new_doctor = Doctor(
                name=name,
                contact=contact,
                specialization='General'  # Default
            )
            db.session.add(new_doctor)
        
        # Admin doesn't need separate profile
        
        db.session.commit()
        
        flash(f'Registration successful as {role}! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')






###----------------logout Route------------------
@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    session.clear()
    flash('Logged out successfully!')
    return redirect(url_for('login'))



#------------------ADMIN ROUTES---------------------#
#------------------ADMIN ROUTES---------------------#

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    pending_appointments = Appointment.query.filter_by(status='Booked').count()
    # Debug line 
    print(f"Stats: D={total_doctors}, P={total_patients}, A={total_appointments}, Pending={pending_appointments}")
    
    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors, 
                         total_patients=total_patients, 
                         total_appointments=total_appointments,
                         pending_appointments=pending_appointments)



@app.route('/admin/add-doctor', methods=['GET', 'POST'])
@admin_required
def add_doctor():
    """Admin add doctor"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        specialization = request.form['specialization']
        contact = request.form['contact']
        department_id = request.form.get('department_id')
         
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('add_doctor'))
        
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role='doctor'
        )
        db.session.add(new_user)
        db.session.flush()
        
        new_doctor = Doctor(
            name=name,
            specialization=specialization,
            contact=contact,
            department_id=department_id if department_id else None
        )
        db.session.add(new_doctor)
        db.session.commit()
        
        flash(f'Doctor {name} added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    departments = Department.query.all()
    return render_template('admin/add_doctor.html', departments=departments)

##------------------------ ADMIN MANAGEMENT ROUTES ----------------###

# View All Doctors
@app.route('/admin/doctors')
@admin_required
def view_doctors():
    """View all doctors"""
    doctors = Doctor.query.all()
    return render_template('admin/view_doctors.html', doctors=doctors)


# Update Doctor
@app.route('/admin/edit-doctor/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_doctor(id):
    """Edit doctor details"""
    doctor = Doctor.query.get_or_404(id)
    
    if request.method == 'POST':
        doctor.name = request.form['name']
        doctor.specialization = request.form['specialization']
        doctor.contact = request.form['contact']
        
        db.session.commit()
        flash(f'Doctor {doctor.name} updated successfully!', 'success')
        return redirect(url_for('view_doctors'))
    
    departments = Department.query.all()
    return render_template('admin/edit_doctor.html', doctor=doctor, departments=departments)


# Delete Doctor
@app.route('/admin/delete-doctor/<int:id>')
@admin_required
def delete_doctor(id):
    """Delete doctor"""
    doctor = Doctor.query.get_or_404(id)
    
    # Also delete associated user account
    user = User.query.filter_by(username=doctor.name).first()
    if user:
        db.session.delete(user)
    
    db.session.delete(doctor)
    db.session.commit()
    
    flash(f'Doctor removed from system!', 'success')
    return redirect(url_for('view_doctors'))


# View All Patients
@app.route('/admin/patients')
@admin_required
def view_patients():
    """View all patients"""
    patients = Patient.query.all()
    return render_template('admin/view_patients.html', patients=patients)


# Delete Patient
@app.route('/admin/delete-patient/<int:id>')
@admin_required
def delete_patient(id):
    """Delete patient"""
    patient = Patient.query.get_or_404(id)
    
    db.session.delete(patient)
    db.session.commit()
    
    flash('Patient removed from system!', 'success')
    return redirect(url_for('view_patients'))


# View All Appointments
@app.route('/admin/appointments')
@admin_required
def view_appointments():
    """View all appointments"""
    appointments = Appointment.query.order_by(Appointment.date.desc()).all()
    return render_template('admin/view_appointments.html', appointments=appointments)


# Search Doctors
@app.route('/admin/search-doctors', methods=['GET', 'POST'])
@admin_required
def search_doctors():
    """Search doctors by name or specialization"""
    if request.method == 'POST':
        search_term = request.form['search']
        
        # Search by name or specialization
        doctors = Doctor.query.filter(
            (Doctor.name.like(f'%{search_term}%')) | 
            (Doctor.specialization.like(f'%{search_term}%'))
        ).all()
        
        return render_template('admin/search_doctors.html', doctors=doctors, search_term=search_term)
    
    return render_template('admin/search_doctors.html', doctors=[], search_term='')


# Search Patients
@app.route('/admin/search-patients', methods=['GET', 'POST'])
@admin_required
def search_patients():
    """Search patients by name, ID or contact"""
    if request.method == 'POST':
        search_term = request.form['search']
        
        # Search by name or contact
        patients = Patient.query.filter(
            (Patient.name.like(f'%{search_term}%')) | 
            (Patient.contact.like(f'%{search_term}%'))
        ).all()
        
        return render_template('admin/search_patients.html', patients=patients, search_term=search_term)
    
    return render_template('admin/search_patients.html', patients=[], search_term='')




##------------------------------ PATIENT ROUTES ---------------------##

@app.route('/patient/dashboard')
@patient_required
def patient_dashboard():
    """Patient dashboard"""
    return render_template('patient/dashboard.html')




###--------------------------- Doctor Routes -------------------###
@app.route('/doctor/dashboard')  
@doctor_required
def doctor_dashboard():
    """Doctor Dashboard"""
    total_appointments = Appointment.query.filter_by(status='Booked').count()
    completed_appointments = Appointment.query.filter_by(status='Completed').count()
    
    return render_template('doctor/dashboard.html', 
                         total_appointments=total_appointments, 
                         completed_appointments=completed_appointments)


###-------------DataBase Initilization --------------------###

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
