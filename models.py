from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, ForeignKey, String, Column,create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin
from sqlalchemy.inspection import inspect

login = LoginManager()
db = SQLAlchemy()

# associate user and service tables with each other
user_service = db.Table('user_service',
					 db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
					 db.Column('service_id', db.Integer, db.ForeignKey('service.id'), primary_key=True)
					 )

class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class UserModel(UserMixin, db.Model, Serializer):
    __tablename__ = 'user'

    # columns
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(100))
    password_hash = db.Column(String())
    role = db.Column(String(80), nullable=False)
    services = db.relationship('ServiceModel', secondary=user_service, backref=db.backref('users'))

    # password hash functions
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    # helper functions
    def serialize(self):
        d = Serializer.serialize(self)
        del d['password_hash']
        del d['services']
        return d

    def __repr__(self):
        return "UserModel: %s %s %s %s" % (self.id, self.username, self.password_hash, self.role)


@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))


class ServiceModel(db.Model, Serializer):
    __tablename__ = 'service'

    # columns
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100))
    api_url = db.Column(String())

    # helper functions
    def serialize(self):
        d = Serializer.serialize(self)
        del d['users']
        return d

    def __repr__(self):
        return "ServiceModel: %s %s %s" % (self.id, self.name, self.api_url)


engine = create_engine('sqlite:///:memory:', pool_recycle=3600, echo=True)
db.Model.metadata.create_all(engine)
Session = db.sessionmaker(bind=engine, expire_on_commit=False, autocommit=False)

class Session(object):
    def __init__(self):
        self.session = Sess()

    def __enter__(self):
        return self.session

    def __exit__(self, *exception):
        if exception[0] is not None:
            self.session.rollback()
        self.session.close()