from flask_wtf import FlaskForm
import datetime
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField, DateField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')

    submit = SubmitField('Войти')
