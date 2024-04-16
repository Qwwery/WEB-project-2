from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired


class UserEditForm(FlaskForm):
    name = StringField('*Имя', validators=[DataRequired()])
    surname = StringField('*Фамилия', validators=[DataRequired()])
    age = IntegerField('*Возраст')
    city = StringField('Город')
    ip_see = BooleanField('Отображать ip во время регистрации', default=False)
