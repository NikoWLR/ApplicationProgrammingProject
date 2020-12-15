from flask import Flask, jsonify, request
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost'
api = Api(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


# Stuff for the log in function

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


#Varaukset

class varaukset(db.Model):
    __tablename__ = 'varaukset'
    varausAika = db.Column(db.DateTime(50), primary_key=True)
    varausPaikka = db.Column(db.String(), nullable=False)
    varausHenkilo = db.Column(db.String(), nullable=False)

    def __init__(self, varausAika, varausPaikka, varausHenkilo):
        self.varausAika = varausAika
        self.varausPaikka = varausPaikka
        self.varausHenkilo = varausHenkilo

#Asiakkaat

class asiakkaat(db.Model):
    __tablename__ = 'asiakkaat'
    AsiakasNimi = db.Column(db.String(50), primary_key=True)
    AsiakasEmail = db.Column(db.String(), nullable=False)

    def __init__(self, asiakasNimi, asiakasEmail):
        self.asiakasNimi = asiakasNimi
        self.asiakasEmail = asiakasEmail


# @app.route('/asiakkaat', methods =['GET'])
# def gasiakkaat():
#   gasiakkaat = asiakkaat.query.all()
#  output = []
# for asiakkaat in gasiakkaat:
#    currAsiakas = {}
#    currAsiakas ['AsiakasNimi']= asiakkaat.AsiakasNimi
#     currAsiakas ['AsiakasEmail']= asiakkaat.AsiakasEmail
#      output.append (currAsiakas)
#   return jsonify(output)

#Työtilat

class tilat(db.Model):
    __tablename__ = 'tyotilat'
    ttNimi = db.Column(db.String(50), primary_key=True)
    ttKuvaus = db.Column(db.String(), nullable=False)
    ttTyyppi = db.Column(db.String(60), nullable=False)

    def __init__(self, ttNimi, ttKuvaus, ttTyyppi):
        self.ttNimi = ttNimi
        self.ttKuvaus = ttKuvaus
        self.ttTyyppi = ttTyyppi


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
    db.create_all()
    app.run(port=5000, debug=True)
