from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, ValidationError, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from app.base.models import User

# login and registration


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Email(message='Проверьте корректность')])
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль',
                             validators=[DataRequired(),
                                         EqualTo('pass_confirm',
                                                 message='Пароли не совпадают')])
    pass_confirm = PasswordField('Повторить пароль', validators=[DataRequired()])

    @staticmethod
    def check_email(field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Адрес эл.почты уже зарегистрирован')
