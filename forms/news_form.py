from flask_wtf import FlaskForm
import datetime
from wtforms import PasswordField, StringField, SubmitField, EmailField, BooleanField, DateField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    name = StringField('*Заголовок', validators=[DataRequired()])
    text = StringField('*Текст новости', validators=[DataRequired()])
    private = BooleanField('Сделать новость приватной')

    submit = SubmitField('Создать новость')
