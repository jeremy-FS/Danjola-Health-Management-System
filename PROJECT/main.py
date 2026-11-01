from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, login_required, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import shutil
import threading
from waitress import serve
import time
# from flask_socketio import SocketIO, emit
# from flask_socketio import SocketIO, send


# ==============================
# INITILZE FLASK APP
# ==============================
app = Flask(__name__)
app.secret_key = 'hmsprojects'

# Database Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "database.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


########### initializing Admin ################################

# def initialize_admin():
#     """Creates a default admin account if not exists"""
#     admin_email = "admin1@gmail.com"   
#     existing_admin = User.query.filter_by(email=admin_email).first()

#     if not existing_admin:
#         admin_user = User(
#             username="Admin1",
#             email=admin_email,
#             usertype="Admin",
#             is_admin=True
#         )
#         admin_user.set_password("admin123") 
#         db.session.add(admin_user)
#         db.session.commit()
#         print("✅ Default admin created: admin1@example.com / admin123")

UPLOAD_FOLDER = "static/uploads/"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# ==============================
# BACKUP SETUP
# ==============================
backup_folder = "backups"
if not os.path.exists(backup_folder):
    os.makedirs(backup_folder)

def backup_database():
    if not os.path.exists("database.db"):
        print("❌ Error: database.db does not exist! Skipping backup...")
        return  # Stop the function if the database doesn't exist

    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        backup_filename = f"database_backup_{timestamp}.db"
        backup_path = os.path.join(backup_folder, backup_filename)

        shutil.copy("database.db", backup_path)
        print(f"✅ Database backup created: {backup_filename}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

def backup_scheduler():
    """Runs the backup script every 24 hours"""
    while True:
        backup_database()
        time.sleep(43200)  # 43200 seconds = 12 hours

# Start the backup scheduler in a separate thread
backup_thread = threading.Thread(target=backup_scheduler, daemon=True)
backup_thread.start()


# ==============================
# DATABASE MODELS
# ==============================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    usertype = db.Column(db.String(50), nullable=False)  # "Admin", "Doctor", "Nurse", etc.
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="Active")  # ✅ New field (Active, Frozen, Deactivated)  

    def set_password(self, password):
        """Hash the password before storing it"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the hashed password"""
        return check_password_hash(self.password_hash, password)



class Patient(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    slot = db.Column(db.String(50), nullable=False)
    disease = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(50), nullable=False, default=datetime.utcnow().strftime('%H:%M:%S'))
    date = db.Column(db.String(50), nullable=False, default=datetime.utcnow().strftime('%Y-%m-%d'))
    dept = db.Column(db.String(50), nullable=False)
    number = db.Column(db.String(10), nullable=False)

    # ✅ Rename conflicting backref names
    appointments = db.relationship('Appointment', backref='patient_appointments', lazy=True)  
    prescriptions = db.relationship('Prescription', backref='patient_prescriptions', lazy=True)  
    diagnoses = db.relationship('Diagnosis', backref='patient_diagnoses', lazy=True)  
    medications = db.relationship('Medication', backref='patient_medications', lazy=True)  
    bills = db.relationship('Bill', backref='patient_bills', lazy=True)


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    speciality = db.Column(db.String(40), nullable=False)
    shift = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(10), nullable=False, unique=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.pid'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_time = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="Scheduled")
    patient = db.relationship("Patient", backref="patient_appointments")  # ✅ Matches Patient Model


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.pid'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    medication = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="Issued")
    patient = db.relationship("Patient", backref="patient_prescriptions")  # ✅ Matches Patient Model


class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.pid'), nullable=False)
    diagnosis = db.Column(db.String(255), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow())
    patient = db.relationship("Patient", backref="patient_diagnoses")  # ✅ Matches Patient Model


class Medication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.pid'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    dosage = db.Column(db.String(50), nullable=False)
    patient = db.relationship("Patient", backref="patient_medications")  # ✅ Matches Patient Model


class Bill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.pid'), nullable=False)
    service = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Unpaid")
    patient = db.relationship("Patient", backref="patient_bills")  # ✅ Matches Patient Model

class BookingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer)
    action = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


# ==============================
# USER AUTHENTICATION
# ==============================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login Successful", "primary")

            # Redirect based on role
            if user.usertype == "Admin":
                return redirect(url_for('admin_dash'))
            elif user.usertype == "Doctor":
                return redirect(url_for('doc_dash'))
            elif user.usertype == "Nurse":
                return redirect(url_for('nur_dash'))
            elif user.usertype == "Receptionist":
                return redirect(url_for('recep_dash'))
            elif user.usertype == "Pharmacist":
                return redirect(url_for('phar_dash'))
            else:
                return redirect(url_for('index'))  # Default redirect

        else:
            flash("Invalid credentials", "danger")
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
@login_required
def signup():
    if current_user.usertype != "Admin":
        flash("Only Admins can create users!", "danger")
        return redirect(url_for('index.html'))
    
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        usertype = request.form.get('usertype')
        password = request.form.get('password')

        new_user = User(username=username, email=email, usertype=usertype)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash(f"{usertype} created successfully!", "success")
        # return redirect(url_for('index')) # uncomment if you wan return home after creating new user

    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout Successful", "warning")
    return redirect(url_for('login'))

# ==============================
# USER AUTHENTICATION
# ==============================

@app.route('/manage-users')
@login_required
def manage_users():
    """Admin view to manage all users."""
    if current_user.usertype != "Admin":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('manage-users.html', users=users)


@app.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user from the system."""
    if current_user.usertype != "Admin":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))
    
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!", "danger")
    return redirect(url_for('manage_users'))


@app.route('/update-user/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    """Update user information."""
    if current_user.usertype != "Admin":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    if user:
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)  # Hash the new password
        db.session.commit()
        flash("User information updated successfully!", "success")

    return redirect(url_for('manage_users'))


@app.route('/freeze-user/<int:user_id>', methods=['POST'])
@login_required
def freeze_user(user_id):
    """Freeze a user's account."""
    if current_user.usertype != "Admin":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    if user:
        user.status = "Frozen"
        db.session.commit()
        flash("User account frozen!", "warning")

    return redirect(url_for('manage_users'))


@app.route('/unfreeze-user/<int:user_id>', methods=['POST'])
@login_required
def unfreeze_user(user_id):
    """Unfreeze a user's account."""
    if current_user.usertype != "Admin":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    if user:
        user.status = "Active"
        db.session.commit()
        flash("User account reactivated!", "success")

    return redirect(url_for('manage_users'))

@app.route('/booking')
def booking():
    return render_template('patient.html')

@app.route('/upgrade-user/<int:user_id>', methods=['POST'])
@login_required
def upgrade_user(user_id):
    """Upgrade user role (e.g., Nurse to Doctor, Doctor to Admin)."""
    if current_user.usertype != "Admin":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))

    user = User.query.get(user_id)
    if user:
        new_role = request.form.get('new_role')
        user.usertype = new_role
        db.session.commit()
        flash(f"User upgraded to {new_role}!", "info")

    return redirect(url_for('manage_users'))


# ==============================
# USER AUTHENTICATION
# ==============================

@app.route('/billing', methods=['GET', 'POST'])
@login_required
def billing():
    if current_user.usertype not in ["Receptionist", "Pharmacist"]:
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        service = request.form.get('service')
        amount = float(request.form.get('amount'))

        new_bill = Bill(patient_id=patient_id, service=service, amount=amount)
        db.session.add(new_bill)
        db.session.commit()
        flash("Bill Added", "success")
    
    unpaid_bills = Bill.query.filter_by(status="Unpaid").all()
    return render_template('billing.html', unpaid_bills=unpaid_bills, patients=Patient.query.all())

@app.route('/mark_paid/<int:id>', methods=['POST'])
@login_required
def mark_paid(id):
    bill = Bill.query.get(id)
    if bill:
        bill.status = "Paid"
        db.session.commit()
        flash("Bill Marked as Paid", "success")
    
    return redirect(url_for('billing'))

@app.route('/admin_reports')
@login_required
def admin_reports():
    if current_user.usertype != "Admin":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))
    
    total_revenue = db.session.query(db.func.sum(Bill.amount)).filter(Bill.status == "Paid").scalar() or 0
    total_unpaid = db.session.query(db.func.sum(Bill.amount)).filter(Bill.status == "Unpaid").scalar() or 0

    patient_expenditures = db.session.query(Patient.name, db.func.sum(Bill.amount)).join(Bill).filter(Bill.status == "Paid").group_by(Patient.name).all()

    all_bills = Bill.query.all()
    return render_template('admin_report.html', total_revenue=total_revenue, total_unpaid=total_unpaid, patient_expenditures=patient_expenditures, all_bills=all_bills)


# ==============================
#       PATIENT MANAGEMENT
# ==============================

@app.route('/patients', methods=['POST', 'GET'])
@login_required
def add_patient():
    """Admin, Doctor, or Nurse can add new patients."""
    if current_user.usertype not in ["Admin", "Doctor", "Nurse", "Receptionist"]:
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))

    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email', '')  # Default to empty string if not provided
        gender = request.form.get('gender')
        age = request.form.get('age')
        slot = request.form.get('slot', 'Not Assigned')  # ✅ Provide default value
        disease = request.form.get('disease', 'Unknown')  # ✅ Default value
        time = datetime.utcnow().strftime('%H:%M:%S')  # ✅ Automatically get current time
        date = datetime.utcnow().strftime('%Y-%m-%d')  # ✅ Automatically get current date
        dept = request.form.get('dept', 'General')
        number = request.form.get('number', '')

        new_patient = Patient(
            name=name,
            email=email,
            gender=gender,
            age=age,
            slot=slot,
            disease=disease,
            time=time,
            date=date,
            dept=dept,
            number=number
        )

        db.session.add(new_patient)
        db.session.commit()
        flash("Patient Registered Successfully!", "success")
        return redirect(url_for('add_patient'))

    patients = Patient.query.all()
    return render_template('manage_patients.html', patients=patients)


@app.route('/edit-patient/<int:pid>', methods=['GET', 'POST'])
@login_required
def edit_patient(pid):
    """Doctors or Nurses can update patient details, diagnosis, and medications."""
    if current_user.usertype not in ["Doctor", "Nurse", "Admin"]:
        flash("Access Denied!", "danger")
        return redirect(url_for('manage_patients'))

    patient = Patient.query.get_or_404(pid)

    if request.method == "POST":
        # Update Patient Info
        patient.name = request.form.get('name')
        patient.email = request.form.get('email')
        patient.gender = request.form.get('gender')
        patient.age = request.form.get('age')

        # Add New Diagnosis (Incremental)
        new_diagnosis = request.form.get('new_diagnosis')
        if new_diagnosis:
            diagnosis_entry = Diagnosis(patient_id=pid, diagnosis=new_diagnosis)
            db.session.add(diagnosis_entry)

        # Add New Medication (Incremental)
        new_medication = request.form.get('new_medication')
        new_dosage = request.form.get('new_dosage')
        if new_medication and new_dosage:
            medication_entry = Medication(patient_id=pid, name=new_medication, dosage=new_dosage)
            db.session.add(medication_entry)

        db.session.commit()
        flash("Patient details updated!", "success")
        return redirect(url_for('view_patient', pid=pid))

    return render_template('edit_patient.html', patient=patient)


@app.route('/delete_patient/<int:pid>', methods=['POST'])
@login_required
def delete_patient(pid):
    patient = Patient.query.get(pid)
    if patient:
        db.session.delete(patient)
        db.session.commit()
        flash("Patient Deleted", "danger")
    return redirect(url_for('manage_patients'))


@app.route('/view-patient/<int:pid>') 
@login_required
def view_patient(pid):
    """View a patient's details."""
    patient = Patient.query.get_or_404(pid)  # ✅ Use `pid`
    prescriptions = Prescription.query.filter_by(patient_id=pid).all()
    diagnoses = Diagnosis.query.filter_by(patient_id=pid).all()
    medications = Medication.query.filter_by(patient_id=pid).all()

    return render_template('patient_details.html', patient=patient,
                           prescriptions=prescriptions, diagnoses=diagnoses, medications=medications)


@app.route('/admin_dash')
@login_required
def admin_dash():
    if current_user.usertype != "Admin":
        flash("Access Denied!", "danger")
        return redirect(url_for('indexl'))
    return render_template('admin-dash.html')


@app.route('/manage_patients', methods=['GET', 'POST'])
@login_required
def manage_patients():
    """Admin, Doctor, or Nurse can view, search, and sort patients."""
    if current_user.usertype not in ["Admin", "Doctor", "Nurse"]:
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))

    # ✅ Search functionality (by name or ID)
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'pid')  # Default sorting by ID

    query = Patient.query

    if search_query:
        query = query.filter(
            (Patient.name.ilike(f"%{search_query}%")) | (Patient.pid == search_query)
        )

    # ✅ Sorting functionality
    if sort_by == "name":
        query = query.order_by(Patient.name.desc())
    elif sort_by == "age":
        query = query.order_by(Patient.age.desc())
    else:  # Default: sort by ID
        query = query.order_by(Patient.pid.desc())

    patients = query.all()
    return render_template('manage_patients.html', patients=patients, search_query=search_query, sort_by=sort_by)


@app.route('/view_appt')
@login_required
def view_appt():
    if current_user.usertype not in ["Doctor", "Nurse"]:
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))
    
    appointments = Appointment.query.all()
    return render_template('view_appt.html', appointments=appointments)

@app.route('/appointments')
@login_required
def appointments():
    if current_user.usertype not in ["Doctor", "Nurse"]:
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))
    
    appointments = Appointment.query.all()
    return render_template('appointment.html', appointments=appointments)

@app.route('/doc_dash')
@login_required
def doc_dash():
    if current_user.usertype != "Doctor":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))
    return render_template('doc-dash.html')


@app.route('/prescriptions')
@login_required
def prescriptions():
   # write out code
   pass
@app.route('/nur_dash')
@login_required
def nur_dash():
    if current_user.usertype != "Nurse":
        flash("Access Denied!", "danger")
        return redirect(url_for("index"))
    return render_template('nur-dash.html')

@app.route('/recep_dash')
@login_required
def recep_dash():
    if current_user.usertype != "Receptionist":
        flash("Access Denied!", "danger")
        return redirect(url_for("index"))
    return render_template('recep-dash.html')

@app.route('/phar-dash')
@login_required
def phar_dash():
    if current_user.usertype != "Pharmacist":
        flash("Access Denied!", "danger")
        return redirect(url_for("index"))
    return render_template('phar-dash.html')

@app.route('/pharmacy')
@login_required
def pharmacy():
    if current_user.usertype != "Pharmacist":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))
    return render_template('pharmacy.html')

@app.route('/medications')
@login_required
def medications():
    drugs = Medication.query.all()
    return render_template('medications.html', drugs=drugs)

@app.route('/inventory', methods=['GET', 'POST'])
@login_required
def inventory():
    if current_user.usertype != "Pharmacist":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))

        new_drug = Medication(name=name, category=category, price=price, stock=stock)
        db.session.add(new_drug)
        db.session.commit()
        flash("Medication Added", "success")
    
    drugs = Medication.query.all()
    return render_template('inventory.html', drugs=drugs)

@app.route('/update_stock/<int:id>', methods=['POST'])
@login_required
def update_stock(id):
    if current_user.usertype != "Pharmacist":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))
    
    drug = Medication.query.get(id)
    if drug:
        new_stock = int(request.form.get('new_stock'))
        drug.stock = new_stock
        db.session.commit()
        flash("Stock Updated", "success")
    
    return redirect(url_for('inventory'))

@app.route('/delete_medication/<int:id>', methods=['POST'])
@login_required
def delete_medication(id):
    if current_user.usertype != "Pharmacist":
        flash("Access Denied!", "danger")
        return redirect(url_for('index'))
    
    drug = Medication.query.get(id)
    if drug:
        db.session.delete(drug)
        db.session.commit()
        flash("Medication Removed", "danger")
    
    return redirect(url_for('inventory'))


# socketio = SocketIO(app, cors_allowed_origins="*")  # Allow cross-origin connections

# # Emit event when a new appointment is booked
# @app.route('/book-appointment', methods=['POST'])
# @login_required
# def book_appointment():
#     patient_id = request.form.get('patient_id')
#     doctor_id = request.form.get('doctor_id')
#     date = request.form.get('date')

#     new_appointment = Appointment(patient_id=patient_id, doctor_id=doctor_id, date=date)
#     db.session.add(new_appointment)
#     db.session.commit()

#     # Notify the doctor in real-time
#     socketio.emit('new_appointment', {'message': 'New appointment request received!'})
    
#     flash("Appointment Booked!", "success")
#     return redirect(url_for('appointments'))

# # Emit event when a payment is made
# @app.route('/make-payment', methods=['POST'])
# @login_required
# def make_payment():
#     bill_id = request.form.get('bill_id')
#     bill = Bill.query.get(bill_id)
#     if bill:
#         bill.status = "Paid"
#         db.session.commit()

#         # Notify the receptionist
#         socketio.emit('new_payment', {'message': 'New payment received!'})

#         flash("Payment Successful!", "success")
#     return redirect(url_for('billing'))


# # Store chat messages in memory (You can use a database for persistence)
# chat_messages = []

# @app.route('/chat')
# @login_required
# def chat():
#     if current_user.usertype not in ["Doctor", "Nurse"]:
#         flash("Access Denied!", "danger")
#         return redirect(url_for('index.html'))
    
#     return render_template('chat.html')

# @socketio.on('message')
# def handle_message(data):
#     """Handles incoming chat messages"""
#     chat_messages.append({'user': current_user.username, 'message': data['message']})
#     send({'user': current_user.username, 'message': data['message']}, broadcast=True)




# ==============================
# DATABASE SETUP
# ==============================

# Ensure database is created inside app context
with app.app_context():
    db.create_all()
    # initialize_admin()

# ==============================
# RUN SERVER
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
    # print("🚀 Server running at http://127.0.0.1:5000")
    # socketio.run(app, host="0.0.0.0", port=5000, debug=True)

