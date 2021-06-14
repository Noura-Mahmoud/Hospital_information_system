from datetime import timedelta
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, Markup
from his import app, db, bcrypt
from his.forms import PRegistrationForm, DRegistrationForm, LoginForm, ContactUsForm, PUpdateAccountForm, DUpdateAccountForm, AppointmentForm
from his.models import Appointment, CTScan, User, ContactUs
from flask_login import login_user, current_user, logout_user, login_required
from his.utils import generate_gcalendar_link
from his import dashboard


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/doctors")
def doctors():
    doctors = User.query.filter_by(role='doctor')
    return render_template('doctors.html', doctors=doctors)

@app.route("/patients")
@login_required
def patients():
    if current_user.role == 'doctor':
        patients = User.query.filter_by(role='patient', doctor_id=current_user.id)
    elif current_user.role == 'admin':
        patients = User.query.filter_by(role='patient')
    return render_template('patients.html', patients=patients)

@app.route("/register_patient", methods=['GET', 'POST'])
def register_patient():
    """register for patients
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = PRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        patient = User(username=form.username.data, email=form.email.data, national_id=form.national_id.data,
                    password=hashed_password, mobile_number=form.mobile_number.data, medical_history=form.medical_history.data,
                    gender=form.gender.data, age=form.age.data, role='patient')
        db.session.add(patient)
        db.session.commit()
        flash('Your patient account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/register_doctor", methods=['GET', 'POST'])
@login_required
def register_doctor():
    """register for doctors
    """
    if current_user.role != 'admin':
        return redirect(url_for('home'))
    form = DRegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, 
        national_id=form.national_id.data, mobile_number=form.mobile_number.data,
        gender=form.gender.data, age=form.age.data, role='doctor')
        db.session.add(user)
        db.session.commit()
        flash('A new doctor has been added! He/She is now able to log in', 'success')
        return redirect(url_for('doctors'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/paccount", methods=['GET', 'POST'])
@login_required
def paccount():
    form = PUpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.mobile_number = form.mobile_number.data
        current_user.gender = form.gender.data
        current_user.age = form.age.data
        current_user.national_id = form.national_id.data
        current_user.medical_history = form.medical_history.data
        scans = []
        if form.scans.data:
            for image in form.scans.data:
                if isinstance(image, str):
                    continue
                picture_file = save_scan(image)
                scan_obj = CTScan(image_file=picture_file, patient_id=current_user.id)
                scans.append(scan_obj)
        db.session.add_all(scans)
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('paccount'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.mobile_number.data = current_user.mobile_number
        form.gender.data = current_user.gender
        form.age.data = current_user.age
        form.national_id.data = current_user.national_id
        form.medical_history.data = current_user.medical_history
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/daccount", methods=['GET', 'POST'])
@login_required
def daccount():
    form = DUpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.mobile_number = form.mobile_number.data
        current_user.gender = form.gender.data
        current_user.age = form.age.data
        current_user.national_id = form.national_id.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('daccount'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.mobile_number.data = current_user.mobile_number
        form.gender.data = current_user.gender
        form.age.data = current_user.age
        form.national_id.data = current_user.national_id
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/patient/<int:patient_id>")
@login_required
def patient(patient_id):
    patient = User.query.filter_by(id=patient_id, role='patient').first_or_404()
    doctor = User.query.filter_by(id=patient.doctor_id, role='doctor').first_or_404()
    return render_template('patient.html', title=patient.username, patient=patient, doctor=doctor)


@app.route("/doctor/<string:username>")
@login_required
def doctor_patients(username):
    if current_user.role == 'admin':
        doctor = User.query.filter_by(username=username, role='doctor').first_or_404()
        return render_template('doctor_patients.html', patients=doctor.patients, doctor=doctor)
    else:
        return redirect(url_for('home'))

@app.route("/message")
@login_required
def message():
    messages = ContactUs.query.all()
    count_messages = len(messages)
    return render_template('messages.html', messages=messages, count_messages=count_messages)

@app.route("/contact_us", methods=['GET', 'POST'])
def contact_us():
    form = ContactUsForm()
    if form.validate_on_submit():
        comment = ContactUs(name=form.name.data, email=form.email.data, mobile_number=form.mobile_number.data, subject=form.subject.data, message=form.message.data)
        db.session.add(comment)
        db.session.commit()
        flash(f'Message sent from {form.name.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('contact_us.html', title='Contact Us', form=form)

@app.route("/reserve_appointment", methods=['GET', 'POST'])
def reserve_appointment():
    """Reserve new appointment
    """
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = AppointmentForm()
    available_drs = [(current_user.doctor_id, User.query.get(current_user.doctor_id).username)] if getattr(current_user, 'doctor_id', None) is not None else\
                [(doc.id, doc.username) for doc in User.query.filter_by(role='doctor')]
    form.doctor_id.choices = available_drs
    if form.validate_on_submit():
        print(
            f'got appointment data !!\n dr {form.doctor_id.data} on {form.appointment_time.data}\n')
        new_app = Appointment(doctor_id=form.doctor_id.data, patient_id=current_user.id,
                              datetime=form.appointment_time.data)
        # assign this dr to this patient
        patient = User.query.get(current_user.id)
        patient.doctor_id = current_user.doctor_id = form.doctor_id.data

        db.session.add(patient)
        db.session.add(new_app)
        db.session.commit()
        doc = User.query.get(form.doctor_id.data)
        gcalendar_link = generate_gcalendar_link(f"Appointment with dr {doc.username}",
                                                 "", form.appointment_time.data, form.appointment_time.data+timedelta(minutes=30))
        flash(Markup(
            f'A new appointment created, <a href="{gcalendar_link}" target="_blank">Add to your calendar</a>'), 'success')
        return redirect(url_for('home'))
    return render_template('reserve_appointment.html', title='Reserve Appointment', form=form)


def save_scan(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/scans_pics', picture_fn)
    form_picture.save(picture_path)
    return picture_fn

@app.route("/scans")
@login_required
def scans():
    scans = CTScan.query.filter_by(patient_id=current_user.id) 
    return render_template('scans.html', title='Patient Scans', scans=scans)


@app.route("/scan/<int:scan_id>")
@login_required
def scan(scan_id):
    scan = CTScan.query.filter_by(id=scan_id, patient_id=current_user.id).first_or_404()
    return render_template('scan.html', title=scan.patient_id, scan=scan)


@app.route("/scan/<int:scan_id>/delete", methods=['POST'])
@login_required
def delete_scan(scan_id):
    scan = CTScan.query.get_or_404(scan_id)
    if scan.patient_id != current_user.id:
        abort(403)
    db.session.delete(scan)
    db.session.commit()
    flash('Your scan has been deleted!', 'success')
    return redirect(url_for('scans'))

@app.route("/appointments")
@login_required
def appointments():
    appointments = []
    if current_user.role == 'doctor':
        appointments = Appointment.query.filter_by(
            doctor_id=current_user.id).all()
    elif current_user.role == 'patient':
        appointments = Appointment.query.filter_by(
            patient_id=current_user.id).all()
    elif current_user.role == 'admin':
        appointments = Appointment.query.all()
    
    doctors = [User.query.get(app.doctor_id) for app in appointments]
    patients = [User.query.get(app.patient_id) for app in appointments]

    results = [(app,doctor,patient) for (app,doctor,patient) in zip(appointments,doctors,patients)]

    return render_template("appointments.html", results=results)

@app.route("/charts")
@login_required
def charts():

    count_patient = User.query.filter_by(role = 'patient').count()
    count_doctor = User.query.filter_by(role = 'doctor').count()
    count_admin = User.query.filter_by(role = 'admin').count()
    app = Appointment.query.count()
    mes = ContactUs.query.count()
    if current_user.role == 'admin':
        return render_template('charts.html', title='Analysis' , count_patient = count_patient ,
                                count_doctor= count_doctor ,count_admin=count_admin , app = app , mes = mes )
    else:
        return redirect(url_for('home'))

@app.route("/dash/")
def dash_app_1():
    return render_template('dashapps/dash_app.html', dash_url=dashboard.URL_BASE)  