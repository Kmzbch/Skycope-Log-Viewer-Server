from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager

login = LoginManager()
db = SQLAlchemy()

# class RegistrationMode(db.Model):
#     __tablename__ = "registration"

#     user_id = db.Column(db.Integer, primary_key=True)
#     service_id = db.Column(db.Integer, primary_key=True)


from sqlalchemy.inspection import inspect

class Serializer(object):

    def serialize(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}

    @staticmethod
    def serialize_list(l):
        return [m.serialize() for m in l]
        
class UserModel(UserMixin, db.Model, Serializer):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String())
    # normal/admin
    role = db.Column(db.String(80), nullable=False)

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
