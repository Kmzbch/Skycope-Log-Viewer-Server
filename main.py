from flask import Flask,flash, render_template,request, Response, redirect, session, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from functools import wraps
from flask_cors import CORS
import json
import jsonpickle

from models import UserModel, ServiceModel, db,login
import config

# create a flask application instance
app = Flask(__name__)
CORS()

# set secret key
app.secret_key = 'yoursecretkey'

# load configurations
app.config.from_object('config')
app.config.from_pyfile('config.py')

# initialize
db.init_app(app)
login.init_app(app)

# create tables and seed data
@app.before_first_request
def create_all():
    db.create_all()

    user1 = UserModel(username="user1", role="normal")
    user1.set_password("user1")
    user2 = UserModel(username="user2", role="admin")
    user2.set_password("user1")
    service1 = ServiceModel(name="Service 1", api_url="/api/services/logs")
    service2 = ServiceModel(name="Service 2", api_url="/api/services/logs")

    user1.services.append(service1)
    user2.services.append(service1)
    user2.services.append(service2)

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(service1)
    db.session.add(service2)

    db.session.commit()

# CORS
@app.after_request
def allow_cross_domain(response: Response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'content-type'
    return response

# routes for main functionalities
@app.route('/api/login', methods=['POST'])
def login():
    # get from request body
    json_data = request.json
    username = json_data['username']
    password = json_data['password']

    # find the user by username
    user = UserModel.query.filter_by(username = username).first()

    # check passowrd and log in
    if user is not None and user.check_password(password):
        login_user(user)
        session['logged_in'] = True
        status = True
    else:
        status = False

    return jsonify({'result': status, 'user': UserModel.serialize(user) })

# routes for support functionalities
@app.route('/api/register', methods=['POST'])
def register():
    json_data = request.json
    username = json_data['username']
    password = json_data['password']
    role = json_data['role'] # normal/admin
    
    # existence check
    if UserModel.query.filter_by(username=username).first():
        return jsonify({'errror': 'username already present' })

    # create a new user
    newUser = UserModel(username=username, role=role)
    newUser.set_password(password)
    try:
        db.session.add(newUser)
        db.session.commit()
        status = 'success'
    except:
        status = 'this user is already registered'

    db.session.close()

    return jsonify({'result': status})

@app.route('/api/logout')
def logout():
    logout_user()
    session.pop('logged_in', None)
    return jsonify({'result': 'success'})

# services
@app.route('/api/services', methods=["GET"])
@login_required
def get_services():
    user_id = request.args.get('user_id')
    user = UserModel.query.get(user_id)
    service_options = [ServiceModel.serialize(x) for x in user.services]

    return jsonify({ 'result': service_options } )

@app.route('/api/services/logs', methods=["GET"])
@login_required
def get_serviceLog():
    service_id = request.args.get('service_id')

    filepath = ""
    lines = []

    if(service_id == "1"):
        filepath = "services/logs/service1-info.log"
    else:
        filepath = "services/logs/service2-info.log"

    with open(filepath) as f:
        lines = f.read()
        return jsonify({'raw' : lines })

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_admin == True:
            return f(*args, **kwargs)
        else:
            flash("You need to be an admin")
            return jsonify({ 'message' : 'only admin allowed!' })
    return wrap

if __name__ == '__main__':
    app.run(
        host=config.HOST, 
        port=config.PORT, 
        debug=True
        )