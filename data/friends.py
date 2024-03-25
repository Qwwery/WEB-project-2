import sqlalchemy
from .db_session import SqlAlchemyBase


class Friends(SqlAlchemyBase):
    __tablename__ = 'friends'

    first_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    second_id = sqlalchemy.Column(sqlalchemy.Integer)
    mans_attitude = sqlalchemy.Column(sqlalchemy.String)

    def __repr__(self):
        return f"first: {self.first_id}; second: {self.second_id}; attitude: {self.mans_attitude}"