import os
from flask import Flask, jsonify, request, abort, g, url_for, make_response
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from datetime import datetime
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
#Konffaukset databasen ja Apin väliseen tiedonsiirtoon.
app.config['SECRET_KEY'] = 'salainen'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Sahkopostin konffaus
app.config.update(
    DEBUG=True,
    #EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = '<email to be used to send emails>',
    MAIL_PASSWORD = '<app password>'
    )

#Osioiden määritys

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost'  #Korvaa postgres oman tietokannan nimellä ja admin omalla salasanalla.
api = Api(app)                                                                   #Tämän jälkeen PyCharmin terminalissa komennot: python -> from app import db -> db.create_all()
db = SQLAlchemy(app)                                                             # Tämän pitäisi luoda tietokanta pgadminiin. Serverin sain itse päälle vaan ajamalla terminalissa komennon: flask run
login_manager = LoginManager()
login_manager.init_app(app)
auth = HTTPBasicAuth()
mail = Mail(app)

#Tyotilojen maara, ajatuksella, etta yhden tyotilan voi varata kerran paivassa, koko paivan ajaksi.
number_of_tables=24

#Kayttajan database-olion luominen, lisatty myos salasanan salaus.

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    telephone = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    email= db.Column(db.String(32))
    name= db.Column(db.String(32))
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    user = User.query.filter_by(username='Niko').first()
    login_user(user)
    return 'You are now logged in!'


@app.route('/logout')
@login_required
def logout():
    return 'You are now logged out!'

@app.route('/home')
@login_required
def home():
    return 'The current user is ' + current_user.username


# Stuff for the Databases

class tilat(db.Model):
    __tablename__ = 'tyotilat'
    ttNimi = db.Column(db.String(50), primary_key=True)
    ttKuvaus = db.Column(db.String(), nullable=False)
    ttTyyppi = db.Column(db.String(60), nullable=False)

    def __init__(self, ttNimi, ttKuvaus, ttTyyppi):
        self.ttNimi = ttNimi
        self.ttKuvaus = ttKuvaus
        self.ttTyyppi = ttTyyppi

class asiakkaat(db.Model):
    __tablename__ = 'asiakkaat'
    AsiakasNimi = db.Column(db.String(50), primary_key=True)
    AsiakasEmail = db.Column(db.String(), nullable=False)

    def __init__(self, asiakasNimi, asiakasEmail):
        self.asiakasNimi = asiakasNimi
        self.asiakasEmail = asiakasEmail

#@app.route('/asiakkaat', methods =['GET'])
#def gasiakkaat():
 #   gasiakkaat = asiakkaat.query.all()
  #  output = []
   # for asiakkaat in gasiakkaat:
    #    currAsiakas = {}
    #    currAsiakas ['AsiakasNimi']= asiakkaat.AsiakasNimi
   #     currAsiakas ['AsiakasEmail']= asiakkaat.AsiakasEmail
  #      output.append (currAsiakas)
 #   return jsonify(output)

@app.route('/tilat', methods=['POST'])
def postTilat():
    tiladata = request.get_json()
    tila = tilat(ttNimi=tiladata['ttNimi'], ttKuvaus=tiladata['ttKuvaus'], ttTyyppi=tiladata['ttTyyppi'])
    db.session.add(tila)
    db.session.commit(tila)
    return jsonify(tiladata)

@app.route('/tilat', methods=['GET'])
def gtilat():
    kaikkitilat = tilat.query.all()
    output = []
    for tyotilat in kaikkitilat:
        currTila = {}
        currTila['ttNimi'] = tyotilat.ttNimi
        currTila['ttKuvaus'] = tyotilat.ttKuvaus
        currTila['ttTyyppi'] = tyotilat.ttTyyppi
        output.append(currTila)
    return jsonify(output)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
