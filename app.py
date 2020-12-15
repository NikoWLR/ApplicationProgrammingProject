from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from database import tilat, asiakkaat
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Admin'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost'
bootstrap = Bootstrap(app)
api = Api(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(Usermixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Login Flaskillä. Eli mitä tietoja kysyttyihin "Fieldeihin" voidaan syöttää.

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    user = User.query.filter_by(username='Niko').first()
    login_user(user)
    return 'You are now logged in!'

@app.route('logout')
@login_required
def logout():
    return 'You are now logged out!'

@app.route('/home')
@login_required
def home():
    return 'The current user is ' + current_user.username

@app.route('/test', methods =['GET'])
def test():
    return {
    'test':'test1'
    }

@app.route('/tilat', methods =['GET'])
def gtilat():
    kaikkitilat = tilat.query.all()
    output = []
    for tyotilat in kaikkitilat:
        currTila = {}
        currTila ['ttNimi']= tyotilat.ttNimi
        currTila ['ttKuvaus']= tyotilat.ttKuvaus
        currTila['ttTyyppi'] = tyotilat.ttTyyppi
        output.append (currTila)
    return jsonify(output)

@app.route('/tilat', methods =['POST'])
def posttilat():
    tilaData = request.get_json(silent=True)
    tila = tilat(ttNimi=tilaData['ttNimi'], ttKuvaus=tilaData['ttKuvaus'], ttTyyppi=tilaData['ttTyyppi'])
    db.session.add(tila)
    db.session.commit
    return jsonify(tilaData)

if __name__ == "__main__":
    app.run(port=5000, debug=True)