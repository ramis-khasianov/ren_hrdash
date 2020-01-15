from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from app.base.models import User

# login and registration


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль',
                             validators=[DataRequired(),
                                         EqualTo('pass_confirm',
                                                 message='Пароли не совпадают')])
    pass_confirm = PasswordField('Повторить пароль', validators=[DataRequired()])


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль',
                                 validators=[DataRequired()])
    pass_confirm = PasswordField('Повторить новый пароль', validators=[DataRequired()])
