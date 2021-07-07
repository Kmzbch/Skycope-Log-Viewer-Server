from flask import Flask,flash, render_template,request, Response, redirect, session, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from functools import wraps
from flask_cors import CORS
import json
from models import UserModel, ServiceModel, RoleModel, db,login
import config
from flask_restful import Resource, Api, abort

# create a flask application instance
app = Flask(__name__)
api = Api(app)

# enable cors
CORS()

# load configurations
app.config.from_object('config')
app.config.from_pyfile('config.py')

# instanciate db and login manager
db.init_app(app)
login.init_app(app)

# create tables and seed data
@app.before_first_request
def create_all():
    db.drop_all()
    db.create_all()

    # pre-defined users and services
    user1 = UserModel(username="user1")
    user1.set_password("user1")
    user2 = UserModel(username="user2")
    user2.set_password("user2")
    service1 = ServiceModel(name="Service 1", api_url="/api/services/logs", access_level=1)
    service2 = ServiceModel(name="Service 2", api_url="/api/services/logs", access_level=2)

    # association between user and service
    role1 = RoleModel(name="normal", access_level=1)
    role2 = RoleModel(name="admin", access_level=2)
    user1.roles.append(role1)
    user2.roles.append(role1)
    user2.roles.append(role2)

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(service1)
    db.session.add(service2)
    db.session.add(role1)
    db.session.add(role2)

    db.session.commit()

# add headers to response for CORS
@app.after_request
def allow_cross_domain(response: Response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    return response

class Login(Resource):
    # routes for main functionalities
    def post(self):
        # get from request body
        json_data = request.json
        username = json_data['username']
        password = json_data['password']

        # find the user by username
        user = UserModel.query.filter_by(username = username).first()

        # check password and log in
        if user is not None and user.check_password(password):
            login_user(user)
            session['logged_in'] = True
        else:
            abort(403)

        return { 'user': UserModel.serialize(user) }, 200

class Logout(Resource):
    def get(self):
        logout_user()
        session.pop('logged_in', None)
        return {'result': 'success'}, 200

class Services(Resource):
    @login_required
    def get(self):
        user_id = request.args.get('user_id')
        user = UserModel.query.get(user_id)
        user_roles = user.roles
        
        service_options = []

        # hard-coded previlege
        for ur in user_roles:
            available_services = ServiceModel.query.filter(ServiceModel.access_level==ur.access_level).all()
            service_options.extend(available_services)

        service_options = [ServiceModel.serialize(x) for x in service_options]

        return { 'result': service_options }, 200

class ServiceLog(Resource):
    @login_required
    def get(self):
        service_id = request.args.get('service_id')

        filepath = ""
        lines = []

        if(service_id == "1"):
            filepath = "services/logs/service1-info.log"
        elif(service_id == "2"):
            filepath = "services/logs/service2-info.log"

        with open(filepath) as f:
            lines = f.read()
            return {'raw' : lines }, 200

class Register(Resource):
    def post(self):
        json_data = request.json
        username = json_data['username']
        password = json_data['password']

        # existence check
        if UserModel.query.filter_by(username=username).first():
            return jsonify({'errror': 'username already present' })

        # create a new user
        newUser = UserModel(username=username)
        newUser.set_password(password)

        try:
            db.session.add(newUser)
            db.session.commit()
        except:
            abort(409)

        db.session.close()

        return { 'result': 'success' }, 201


# decorator for admin access (not used)
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_admin == True:
            return f(*args, **kwargs)
        else:
            flash("You need to be an admin")
            return jsonify({ 'message' : 'only admin allowed!' })
    return wrap

# add resources
api.add_resource(Login, '/api/login')
api.add_resource(Logout, '/api/logout')
api.add_resource(Register, '/api/register')
api.add_resource(Services, '/api/services')
api.add_resource(ServiceLog, '/api/services/logs')

if __name__ == '__main__':
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
        )