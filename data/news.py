import datetime

import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase, UserMixin):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    data = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    data_str = sqlalchemy.Column(sqlalchemy.String, default='')

    private = sqlalchemy.Column(sqlalchemy.Boolean, default=False)