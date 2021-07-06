from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, ForeignKey, String, Column,create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.inspection import inspect
from flask_login import LoginManager
from flask_login import UserMixin

login = LoginManager()
db = SQLAlchemy()

#Base = declarative_base()

    
class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]


class UserModel(UserMixin, db.Model, Serializer):
    __tablename__ = 'user'

    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(100))
    password_hash = db.Column(String())
    role = db.Column(String(80), nullable=False)

    services = db.relationship("ServiceModel", backref="user")

    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

    def serialize(self):
        d = Serializer.serialize(self)
        del d['password_hash']
        return d

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))


class ServiceModel(db.Model, Serializer):
    __tablename__ = 'service'

    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100))
    api_url = db.Column(String())
    user_id = db.Column(Integer, ForeignKey('user.id'))

    def serialize(self):
        d = Serializer.serialize(self)
        return d

engine = create_engine('sqlite:///:memory:', pool_recycle=3600, echo=True)
db.Model.metadata.create_all(engine)
Sess = db.sessionmaker(bind=engine, expire_on_commit=False, autocommit=False)

class Session(object):
    def __init__(self):
        self.session = Sess()

    def __enter__(self):
        return self.session

    def __exit__(self, *exception):
        if exception[0] is not None:
            self.session.rollback()
        self.session.close()