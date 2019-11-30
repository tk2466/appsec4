from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError
from models import *

class RegistrationForm(FlaskForm):
    """Registration form"""

    username = StringField('Username',
                           validators=[DataRequired(message="Registration Failure. Username required"),
                                       Length(min=4, max=25, message="Registration Failure. Username must be between 4 and 25 characters")],
                           # tags can be defined here like so:
                           # render_kw={"placeholder": "Username"}
                           id="uname")
    phonenumber = StringField('Phone Number',
                              validators=[DataRequired(message="Registration Failure. Phonenumber required"),
                                          Length(min=11, max=11,
                                                 message="Registration Failure. Phone Number must be 11 characters long")],
                              id="2fa")
    password = PasswordField('Password',
                             validators=[DataRequired(message="Registration Failure. Password required")],
                             id="pword")

    submit_button = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    """ Login form """

    username = StringField('Username',
                           validators=[DataRequired(message="Login Failure. Username required")], id="uname")
    password = PasswordField('Password',
                             validators=[DataRequired(message="Login Failure. Password required")], id="pword")
    phonenumber = StringField('Phone Number',
                              validators=[DataRequired(message="Login Failure. Two-factor required")], id="2fa")
    remember = BooleanField('Remember Me')
    submit_button = SubmitField('Login')


class CheckSpelling(FlaskForm):
    """ Spell Checker form """

    inputtext = TextAreaField('Input Text',
                           validators=[DataRequired(message="Spell check Failure. Input text required")], id="inputtext")

    submit_button = SubmitField('Check Spelling')


class HistoryForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(message="Username required")], id="userquery")
    submit_button = SubmitField('Search')


class LoginHistoryForm(FlaskForm):
    uid = StringField('User ID', validators=[DataRequired(message="User ID required")], id="userid")
    submit_button = SubmitField('Search')