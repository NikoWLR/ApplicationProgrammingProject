from flask import Flask, jsonify, request
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
# from database import tilat
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost'  #Korvaa postgres oman tietokannan nimella ja admin omalla salasanalla.
api = Api(app)                                                                   #Taman jalkeen PyCharmin terminalissa komennot: python -> from app import db -> db.create_all()
db = SQLAlchemy(app)                                                             # Taman pitaisi luoda tietokanta pgadminiin. Serverin sain itse paaalle vaan ajamalla terminalissa komennon: flask run
login_manager = LoginManager()
login_manager.init_app(app)


# Stuff for the log in function1

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)


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

@app.route('/asiakkaat', methods =['GET'])
def gasiakkaat():
    kaikkiAsiakkaat = asiakkaat.query.all()
    output = []
    for asiakkaat in kaikkiAsiakkaat:
        currAsiakas = {}
        currAsiakas ['AsiakasNimi']= asiakkaat.AsiakasNimi
        currAsiakas ['AsiakasEmail']= asiakkaat.AsiakasEmail
        output.append (currAsiakas)
    return jsonify(output)

@app.route('/tilat', methods=['POST'])
def postTilat():
    tiladata = request.get_json()
    tila = tilat(ttNimi=tiladata['ttNimi'], ttKuvaus=tiladata['ttKuvaus'], ttTyyppi=tiladata['ttTyyppi'])
    db.session.add(tila)
    db.session.commit()
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


#@app.route('/tilat', methods=['POST'])
#def postTilat():
 #   tiladata = request.get_json()
  #  tila = tilat(ttNimi=tiladata['ttNimi'], ttKuvaus=tiladata['ttKuvaus'], ttTyyppi=tiladata['ttTyyppi'])
   # db.session.add(tila)
    #db.session.commit(tila)
    #return jsonify(tiladata)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
