
from flask import Flask,render_template,request,redirect, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from models import UserModel,db,login

app = Flask(__name__)
app.secret_key = 'xyz'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login.init_app(app)
login.login_view = 'login'

@app.before_first_request
def create_all():
    db.create_all()
    
@app.route('/blogs')
@login_required
def blog():
    return render_template('blog.html')

@app.route('/login', methods=['POST'])
def login():
    json_data = request.json
    print(json_data)
    email = json_data['email']
    password = json_data['password']
    user = UserModel.query.filter_by(email = email).first()
    if user is not None and user.check_password(password):
        login_user(user)
        # session['logged_in'] = True
        status = True
    else:
        status = False
    return jsonify({'result': status})

@app.route('/register', methods=['POST'])
def register():
    json_data = request.json

    email = json_data['email']
    username = json_data['username']
    password = json_data['password']

    if UserModel.query.filter_by(email=email).first():
        return ('Email already Present')

    user = UserModel(email=email, username=username)
    user.set_password(password)

    try:
        db.session.add(user)
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

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
