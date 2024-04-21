import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

categories = orm.relationship("Category",
                              secondary="association",
                              backref="weapons")


class Weapons(SqlAlchemyBase):
    __tablename__ = 'weapons'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    assault_rifle = sqlalchemy.Column(sqlalchemy.String)
    pistol = sqlalchemy.Column(sqlalchemy.String)
    submachine_gun = sqlalchemy.Column(sqlalchemy.String)
    shotgun_rifle = sqlalchemy.Column(sqlalchemy.String)
    device = sqlalchemy.Column(sqlalchemy.String)
    melee = sqlalchemy.Column(sqlalchemy.String)
    heavy = sqlalchemy.Column(sqlalchemy.String)
    machine_gun = sqlalchemy.Column(sqlalchemy.String)
    sniper_rifle = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')
