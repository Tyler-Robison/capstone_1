from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import InputRequired, Email, Length


class RegisterForm(FlaskForm):
    """Registration Form"""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    email = StringField('E-mail', validators=[Email(), InputRequired()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])


class LoginForm(FlaskForm):
    """Login Form"""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class SearchForm(FlaskForm):
    """Form for searching"""
    address = StringField('Address', validators=[InputRequired()])
    radius = SelectField('Miles Away', coerce=int)

class UserEditForm(FlaskForm):
    """Form for editing profile"""    
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('E-mail', validators=[Email(), InputRequired()])
    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class ChangePwdForm(FlaskForm):
    """Form for changing password"""    
    old_password = PasswordField('Please Enter Your Password', validators=[InputRequired()])
    new_password = PasswordField('New Password', validators=[InputRequired(), Length(min=6)])
