import sqlalchemy
from .db_session import SqlAlchemyBase


class Messages(SqlAlchemyBase):
    __tablename__ = 'messages'

    id_message = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.Integer)
    before = sqlalchemy.Column(sqlalchemy.Integer)
    js_message = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f"author({self.author}) -> before({self.before}) '{self.js_message}'"
