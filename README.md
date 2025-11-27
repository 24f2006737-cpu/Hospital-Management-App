# 🏥 Hospital Management System

A web-based Hospital Management System built with Flask and SQLAlchemy for managing patients, doctors, appointments, and treatments efficiently.

## 📋 Project Description

This Hospital Management System is designed to streamline hospital operations by providing a digital platform for managing:
- **Patient Records** - Store and manage patient information
- **Doctor Profiles** - Maintain doctor details and specializations
- **Appointments** - Schedule and track patient-doctor appointments
- **Treatments** - Record diagnoses, prescriptions, and medical notes
- **Departments** - Organize doctors by medical departments

## 🛠️ Technologies Used

- **Backend:** Flask (Python)
- **Database:** SQLite with Flask-SQLAlchemy ORM
- **Frontend:** Jinja2 Templates, HTML5, CSS3, Bootstrap 5
- **Authentication:** Werkzeug Security (Password Hashing)

## 📊 Database Schema

The system includes 6 main tables:
- `users` - Admin, Doctor, and Patient login credentials
- `departments` - Hospital departments/specializations
- `patients` - Patient personal information
- `doctors` - Doctor profiles linked to departments
- `appointments` - Patient-doctor appointment bookings
- `treatments` - Medical records for completed appointments

## 🚀 Installation & Setup

1. Create the repository:
git clone https://github.com/24f2006737/Hospital-Management-App.git
cd Hospital-Management-App/hospital_management
2. Create virtual environment:  python -m venv venv  venv\Scripts\activate # Windows
3. Install dependencies: pip install flask flask-sqlalchemy werkzeug
4. Run the application: python app.py
5. Access the application:  Open browser: http://127.0.0.1:5000
6. 
