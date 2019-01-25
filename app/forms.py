from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask_wtf.file import FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import DataRequired, EqualTo, ValidationError

from app import profiles
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    photo = FileField(validators=[FileAllowed(profiles, u'Image only!'), FileRequired(u'File was empty!')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.select().where(User.username == username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
    #
    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different email address.')

class StreamForm(FlaskForm):
    chatID = StringField('chatID',validators=[DataRequired()])
    streamID = StringField('streamID',validators=[DataRequired()])
    file = FileField('file',validators=[FileRequired()])
    fin = BooleanField('final')
