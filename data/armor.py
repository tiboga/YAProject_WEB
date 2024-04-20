import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

categories = orm.relationship("Category",
                              secondary="association",
                              backref="weapons")


class Armor(SqlAlchemyBase):
    __tablename__ = 'armor'
    
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    clothes = sqlalchemy.Column(sqlalchemy.String)
    combat = sqlalchemy.Column(sqlalchemy.String)
    combined = sqlalchemy.Column(sqlalchemy.String)
    device = sqlalchemy.Column(sqlalchemy.String)
    scientist = sqlalchemy.Column(sqlalchemy.String)
    
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
