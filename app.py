from flask import Flask, jsonify, request, abort, g, url_for, make_response
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)
#Konffaukset databasen ja Apin väliseen tiedonsiirtoon.
app.config['SECRET_KEY'] = 'salainen'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost'  #Korvaa postgres oman tietokannan nimellä ja admin omalla salasanalla.
api = Api(app)                                                                   #Tämän jälkeen PyCharmin terminalissa komennot: python -> from app import db -> db.create_all()
db = SQLAlchemy(app)                                                             # Tämän pitäisi luoda tietokanta pgadminiin. Serverin sain itse päälle vaan ajamalla terminalissa komennon: flask run
login_manager = LoginManager()
login_manager.init_app(app)
auth = HTTPBasicAuth()
mail = Mail(app)

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

#Varauksen olio-ohjelma tietokannalle.
class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    telephone = db.Column(db.String(32))
    date = db.Column(db.DateTime, index=True)


#Salasanan tsekkaus

@auth.verify_password
def verify_password(telephone, password):
    # try to authenticate with username/password
    user = User.query.filter_by(telephone=telephone).first()
    if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

#Virheiden varalle
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Voi juma, jotai män piellee'}), 404)

#Reitti jota pitkin uusi käyttäjä lisätään. Käyttäjällä voi kyllä olla useampi sähkäri..
@app.route('/api/user/add', methods=['POST'])
def new_user():
    telephone = request.json.get('telephone')
    password = request.json.get('password')
    email = request.json.get('email')
    name = request.json.get('name')
    if telephone is None or password is None or email is None or name is None:
        abort(make_response(jsonify(message="Missing arguments"), 400))    # missing arguments
    if User.query.filter_by(telephone=telephone).first() is not None:
        abort(make_response(jsonify(message="A user with the same telephone number exists!"), 400))    # existing user
    user = User(telephone=telephone,email=email,name=name)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'status': 'User added successfully!'}), 201)


@app.route('/api/user/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'telephone': user.telephone})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.telephone})


@app.route('/api/reservation', methods=['POST'])
@auth.login_required
def make_reservation():
    date = request.json.get('date')
    user_id = request.authorization.username

    # getting user email
    user = User.query.filter_by(telephone=user_id).first()

    # Processing date and creating python datetime object
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    reservations = Reservation.query.filter_by(date=date_obj).count()

    if reservations < number_of_tables:
        # More resevations can be made
        reservation = Reservation(telephone=user_id, date=date_obj)
        db.session.add(reservation)
        db.session.commit()

        # Sending the email
        try:
            msg = Message("Reservation made successfully!",
                          sender="restaurant@gmail.com",
                          recipients=[user.email])
            message_string = """Hi {0},\nYou have made a reservation successfully in our restaurant on {1}.\nFeel free to contact us for any inquiries. Thank you.\nRestaurant Staff"""
            msg.body = message_string.format(user.name, date)
            mail.send(msg)
            return (jsonify({'status': 'Reservation added successfully'}))

        except Exception as e:
            return (jsonify({'status': 'Reservation added successfully but email not sent'}))


    else:
        # Cannot make anymore reservations
        return (jsonify({
                            'status': 'Reservation adding failed !. We cannot accomodate any more reservations for the mentioned date'}))
# Stuff for the log in function

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)

#TÄSTÄ ALKAA VANHA
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
