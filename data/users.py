import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class User(SqlAlchemyBase):

    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,

                           primary_key=True, autoincrement=True)

    name_channel = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    message = sqlalchemy.Column(sqlalchemy.String, nullable=True)
