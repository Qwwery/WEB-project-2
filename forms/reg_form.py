from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField, DateField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired


class RegForm(FlaskForm):
    name = StringField('*Имя', validators=[DataRequired()])
    surname = StringField('*Фамилия', validators=[DataRequired()])
    age = IntegerField('*Возраст')
    city = StringField('Город')
    email = EmailField('*Почта', validators=[DataRequired()])
    password = PasswordField('*Пароль', validators=[DataRequired()])
    repeat_password = PasswordField('*Повторите пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Создать аккаунт')
