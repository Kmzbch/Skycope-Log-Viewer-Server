from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from sqlalchemy import Integer, ForeignKey, String, Column,create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.inspection import inspect
from werkzeug.security import generate_password_hash, check_password_hash

login = LoginManager()
db = SQLAlchemy()

class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]

# role management by association table
user_role = db.Table('user_role',
					 db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
					 db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True)
					 )

class RoleModel(db.Model, Serializer):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    access_level = db.Column(db.Integer, nullable=False)

    # helper functions
    def serialize(self):
        d = Serializer.serialize(self)
        del d['users']
        return d

    def __repr__(self):
        return "RoleModel: %s %s " % (self.id, self.name)


class UserModel(UserMixin, db.Model, Serializer):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String())

    roles = db.relationship('RoleModel', secondary=user_role, backref=db.backref('users'))

    # password hash functions
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    # helper functions
    def serialize(self):
        d = Serializer.serialize(self)
        # del d['password_hash']
        del d['roles']
        return d

    def __repr__(self):
        return "UserModel: %s %s %s" % (self.id, self.username, self.password_hash)


@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))


class ServiceModel(db.Model, Serializer):
    __tablename__ = 'service'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    api_url = db.Column(db.String())
    access_level = db.Column(db.Integer)

    # helper functions
    def serialize(self):
        d = Serializer.serialize(self)
        return d

    def __repr__(self):
        return "ServiceModel: %s %s %s %s" % (self.id, self.name, self.api_url, self.access_level)
