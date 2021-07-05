from flask import Flask,flash, render_template,request,redirect, session, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from functools import wraps
from models import UserModel,db,login
import config

app = Flask(__name__)

app.secret_key = 'yoursecretkey'
app.config.from_object('config')
app.config.from_pyfile('config.py')

db.init_app(app)
login.init_app(app)
login.login_view = 'login'

@app.before_first_request
def create_all():
    db.create_all()

# routes for main functionalities
@app.route('/login', methods=['POST'])
def login():
    # get from request body
    json_data = request.json
    email = json_data['email']
    password = json_data['password']

    # find the user by email
    user = UserModel.query.filter_by(email = email).first()

    # check passowrd and log in
    if user is not None and user.check_password(password):
        login_user(user)
        session['logged_in'] = True
        status = True
    else:
        status = False
    return jsonify({'result': status})

# routes for support functionalities
@app.route('/register', methods=['POST'])
def register():
    json_data = request.json
    username = json_data['username']
    password = json_data['password']
    role = json_data['role'] # normal/admin

    # existence check
    if UserModel.query.filter_by(email=email).first():
        return jsonify({'errror': 'email already present' })

    # create a new user
    newUser = UserModel(email=email, username=username, role=role)
    newUser.set_password(password)
    try:
        db.session.add(newUser)
        db.session.commit()
        status = 'success'
    except:
        status = 'this user is already registered'

    db.session.close()

    return jsonify({'result': status})

@app.route('/logout')
def logout():
    logout_user()
    session.pop('logged_in', None)
    return jsonify({'result': 'success'})

# services
# # get log
# @app.route('/services', methods=["GET"])
# @login_required
# def get_services():
#     # json_data = request.json
#     # id = json_data['id']
#     return jsonify({ 'result': "!!!"} )
@app.route('/services/{id}', methods=["GET"])
@login_required
def get_service(id):
    # json_data = request.json
    # id = json_data['id']
    return jsonify({ 'result': "!!!"} )

@app.route('/services/{id}/log', methods=["GET"])
@login_required
def get_serviceLog(id):
    # json_data = request.json
    # id = json_data['id']
    return jsonify({ 'result': "!!!"} )


# decorators
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.is_admin == True:
            return f(*args, **kwargs)
        else:
            flash("You need to be an admin")
            return jsonify({ 'message' : 'only admin allowed!' })
    return wrap

# test
@app.route('/multi/<int:num>')
@login_required
def multiTen(num):
    return jsonify({ 'result' : num * 10 })

@app.route('/add/<int:num>')
@admin_required
def addTwo(num):
    return jsonify({ 'result' : num + 2 })

if __name__ == '__main__':
    app.run(
        host=config.HOST, 
        port=config.PORT, 
        debug=True
        )