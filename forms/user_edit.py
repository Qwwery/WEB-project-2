from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import DataRequired


class UserEditForm(FlaskForm):
    name = StringField('*Имя', validators=[DataRequired()])
    surname = StringField('*Фамилия', validators=[DataRequired()])
    age = IntegerField('*Возраст')
    city = StringField('Город')
    setup_see = BooleanField('Отображать шутку', default=False)
    domen = StringField('Псевдоним')
    update_setup = BooleanField('Изменить шутку', default=False)
