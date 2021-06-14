from datetime import datetime, date, time, timedelta
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, MultipleFileField, IntegerField
from wtforms.fields.html5 import DateTimeField, DateTimeLocalField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Required, ValidationError
from his.models import User, Appointment


class PRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    mobile_number = StringField('Mobile Number', validators=[
                                DataRequired(), Length(11)])
    national_id = StringField('National ID Number', validators=[
                              DataRequired(), Length(14)])
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[
        ('male', 'male'), ('female', 'female')], validators=[DataRequired()])
    medical_history = TextAreaField('Medical History', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        doctor = User.query.filter_by(username=username.data).first()
        if doctor:
            raise ValidationError(
                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        doctor = User.query.filter_by(email=email.data).first()
        if doctor:
            raise ValidationError(
                'That email is taken. Please choose a different one.')

    def validate_national_id(self, national_id):
        doctor = User.query.filter_by(national_id=national_id.data).first()
        if doctor:
            raise ValidationError(
                'That national_id is taken. Please choose a different one.')

class DRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    mobile_number = StringField('Mobile Number', validators=[
                                DataRequired(), Length(11)])
    national_id = StringField('National ID Number', validators=[
                              DataRequired(), Length(14)])
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[
        ('male', 'male'), ('female', 'female')], validators=[DataRequired()])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        doctor = User.query.filter_by(username=username.data).first()
        if doctor:
            raise ValidationError(
                'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        doctor = User.query.filter_by(email=email.data).first()
        if doctor:
            raise ValidationError(
                'That email is taken. Please choose a different one.')

    def validate_national_id(self, national_id):
        doctor = User.query.filter_by(national_id=national_id.data).first()
        if doctor:
            raise ValidationError(
                'That national_id is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class AppointmentForm(FlaskForm):
    available_drs = [(doc.id, doc.username)
                     for doc in User.query.filter_by(role='doctor')]

    doctor_id = SelectField(
        'Doctor', choices=available_drs, validators=[DataRequired()])
    appointment_time = DateTimeLocalField(

        'Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    # appointment_time = DateTimeField('Time', validators=[DataRequired()])
    submit = SubmitField('Reserve')

    def validate_appointment_time(self, appointment_time):
        # check if dr is available at that time
        # query appointment for any for the current doctor
        appointment_time = appointment_time.data
        reserved = Appointment.query.filter_by(doctor_id=int(
            self.doctor_id.data)).filter(Appointment.datetime.between(appointment_time-timedelta(minutes=29), appointment_time+timedelta(minutes=29))).first()
        if reserved:
            dr = User.query.get(int(self.doctor_id.data))
            raise ValidationError(
                f'Dr {dr.username} is not available at that time. Please choose a different one.')


class PUpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    mobile_number = StringField('Mobile Number', validators=[
                                DataRequired()])
    gender = SelectField('Gender', choices=[
        ('male', 'male'), ('female', 'female')], validators=[DataRequired()])
    scans = MultipleFileField('Upload your scans', validators=[
        FileAllowed(['jpg', 'png'])])

    age = IntegerField('Age', validators=[DataRequired()])
    national_id = StringField('National ID Number', validators=[
                              DataRequired(), Length(14)])
    medical_history = TextAreaField('Medical History', validators=[DataRequired()])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'That email is taken. Please choose a different one.')

    # def validate_national_id(self, national_id):
    #     if national_id.data != current_user.national_id:
    #         user = User.query.filter_by(national_id=national_id.data).first()
    #         if user:
    #             raise ValidationError(
    #                 'That national_id is taken. Please choose a different one.')

class DUpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    mobile_number = StringField('Mobile Number', validators=[
                                DataRequired()])
    gender = SelectField('Gender', choices=[
        ('male', 'male'), ('female', 'female')], validators=[DataRequired()])

    age = IntegerField('Age', validators=[DataRequired()])
    national_id = StringField('National ID Number', validators=[
                              DataRequired(), Length(14)])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'That email is taken. Please choose a different one.')

    # def validate_national_id(self, national_id):
    #     if national_id.data != current_user.national_id:
    #         user = User.query.filter_by(national_id=national_id.data).first()
    #         if user:
    #             raise ValidationError(
    #                 'That national_id is taken. Please choose a different one.')

class ContactUsForm(FlaskForm):
    name = StringField('Name', validators=[
                       DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    mobile_number = StringField('Mobile Number', validators=[
                                DataRequired(), Length(11)])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Send Message')
