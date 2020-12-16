#Haetaan tarvittavat moduulitl.
import os
from flask import Flask, jsonify, request, abort, g, url_for, make_response, render_template
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from datetime import datetime
from flask_mail import Mail, Message


app = Flask(__name__)
# Konffaukset databasen ja Apin väliseen tiedonsiirtoon.
app.config['SECRET_KEY'] = 'salainen'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost'  #Korvaa postgres oman tietokannan nimellä ja admin omalla salasanalla.
api = Api(app)                                                                   #Tämän jälkeen PyCharmin terminalissa komennot: python -> from app import db -> db.create_all()
db = SQLAlchemy(app)                                                             # Tämän pitäisi luoda tietokanta pgadminiin. Serverin sain itse päälle vaan ajamalla terminalissa komennon: flask run
login_manager = LoginManager()
login_manager.init_app(app)
auth = HTTPBasicAuth()
mail = Mail(app) #Ei varsinaisessa käytössä, koska Email-domainia ei ole olemassa.



# Työtilojen määrä, ajatuksella, että yhden työtilan voi varata kerran päivässä, koko päivan ajaksi.

number_of_tables=24

#Callback jotta käyttäjän objekti voidaan ladata ID:n mukaisesti tietokannasta.
#Tässä vaiheessa koskee lähinnä Admin-toimintoja vaativaa osiota.

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

#Callback toiminto, joka tarkistaa kahden argumentin yhteensopivuuden. Olemme käyttäneen
#asiakkaa db-modelissa hash_password callbackia, joten tätä ei tarvita. (periaatteessa)

@auth.verify_password
def verify_password(telephone, password):
    #Voi tarvittaessa kokeilla user-id:llä tai emaililla, jos toimii.
    user = User.query.filter_by(telephone=telephone).first()
    if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

#Tämä route palauttaa virhesivun, jos esim salasana ei täsmää tai käytetään vanhaa versiointia.

@app.errorhandler(404)
def user_loader(error):
    return render_template('404.html')





#Alkavassa koodissa on osoita, joita voidaan lainata tarpeen mukaan.  Jos tulee olemaan vain yksi admin-käyttis,
#Ei alla oleva app.route ole kovin oleellinen.


# Route, jota pitkin uusi käyttäjä lisätään. Käyttäjällä voi kyllä olla useampi sähköposti.
@app.route('/api/user/add', methods=['POST'])
def new_user():
    telephone = request.json.get('telephone')
    password = request.json.get('password')
    email = request.json.get('email')
    name = request.json.get('name')
    if telephone is None or password is None or email is None or name is None:
        abort(make_response(jsonify(message="Missing arguments"), 400))    # missing arguments
    if User.query.filter_by(telephone=telephone).first() is not None:
        abort(make_response(jsonify(message="A user with the same telephone number exists!"), 400))    # Jollain toisella sama numero
    user = User(telephone=telephone,email=email,name=name)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'status': 'User added successfully!'}), 201)

#Get-pyyntö käyttäjän id:tä varten. Jos ei pysty hakemaan db:stä, palauttaa bad requestin.

@app.route('/api/user/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'telephone': user.telephone})

#DB:n tietoihin pääsy kirjautuneena.

@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.telephone})

#Tätä kautta käyttäjä voi suorittaa varauspyynnön, vain kun on kirjautuneena varausjärjestelmään.

@app.route('/api/reservation', methods=['POST'])
@auth.login_required
def make_reservation():
    date = request.json.get('date')
    user_id = request.authorization.username

    # getting user email
    user = User.query.filter_by(telephone=user_id).first()

    #Määritetään aika-objekti ja liitetään se varausmuuttujaan.
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    reservations = Reservation.query.filter_by(date=date_obj).count()

    if reservations < number_of_tables:
        #Jos varausten määrä on pienempi, kuin vapaana olevien tilojen määrä, varaus voidaan suorittaa.
        reservation = Reservation(telephone=user_id, date=date_obj)
        db.session.add(reservation)
        db.session.commit()

        #Jos varaajan pyyntö menee läpi, voidaan sähköpostista lähettää automaattivastaus.
        #S.posti-palvelinta ei ole kuitenkaan määritetty, koska mitään sopivaa domainia ei ole olemassa/
        #Eikä tämä ole projektin ajanhallinnan kannalta välttämätön ominaisuus.
        try:
            msg = Message("Workspace reserved, Thank you!",
                          sender="info@TUASspacemanger.fi",
                          recipients=[user.email])
            message_string = """Hello {0},\nReservation has been made on {1}.\n For any questions, reply to this mail. \nTUAS Workspace reservation Team."""
            msg.body = message_string.format(user.name, date)
            mail.send(msg)
            return (jsonify({'status': 'Reservation added successfully'}))

        except Exception as e:
            return (jsonify({'status': 'Reservation added successfully but email not sent'}))

        #Jos varausta ei voida suorittaa, toiminta palauttaa viestin.
    else:
        return (jsonify({'status': 'Cannot make reservation, workspace not available.'}))

#Flask-loginiin tarvitta käyttäjän db.model. UserMixin tarkoitus on implementoida
#kirjautumiseen tarvittavia ominaisuuksi, jotta esimerkiksi is_authenticated voidaan
#tuoda ja tarkistaa kirjautumistiedot. Helpottaa, sillä kaikkia metodeita ei tarvitse kirjoittaa itse.

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(64))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User{}>'.format(self.username)


#Asiakkaat-olion luominen ja siihen tarvittava data. Salasanan tallentaminen tekstinä on epäturvallista, joten
#määritimme salasanat Passlib CryptContext riippuvaisiksi. Hash:iä vertaillaan esimerkiksi aina tietokantaan
#tallennettuun dataan ja login on mahdollista palauttaa vain, jos tämä vertailu onnistui.

class asiakkaat(db.Model):
    __tablename__ = 'Asiakkaat'
    id = db.Column(db.Integer, primary_key=True)
    puhelin = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    email= db.Column(db.String(32))
    nimi= db.Column(db.String(32))

    def __init__(self, id, puhelin, nimi, email):
        self.id = id
        self.puhelin = puhelin
        self.email = email
        self.nimi = nimi

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

#Tämä route hakee KAIKKIEN asiakkaiden tiedot tietokannasta.

@app.route('/asiakkaat', methods =['GET'])
def gasiakkaat():
    kaikkiasiakkaat = asiakkaat.query.all()
    output = []
    for asiakastiedot in kaikkiasiakkaat:
        currAsiakas = {}
        currAsiakas ['id']= asiakastiedot.id
        currAsiakas ['puhelin']= asiakastiedot.puhelin
        currAsiakas['email'] = asiakastiedot.email
        currAsiakas['nimi'] = asiakastiedot.nimi
        output.append(currAsiakas)
    return jsonify(output)

#Uuden asiakkaan luominen tietokantaan. HTML-tiedostossa, GUI:ssa voidaan implementoida siten, että
#tietokannan data on liitetty formiin, joka voitaisiin submit-nappia painamalla lisätä tietokantaan.

@app.route('/asiakkaat', methods=['POST'])
def postAsiakkaat():
    asiakasdata = request.get_json()
    asiakas = asiakkaat(id=asiakasdata['id'], puhelin=asiakasdata['puhelin'], email=asiakasdata['email'], nimi=asiakasdata['nimi'])
    db.session.add(asiakas)
    db.session.commit()
    return jsonify(asiakasdata)

#Asiakastiedon muokkaaminen tietokannassa jo olevaan tableen.

@app.route('/asiakkaat/<int:id>', methods=['PUT'])
def updateAsiakkaat(id):
    asiakasdata = request.get_json()
    currAsiakas = asiakasdata('id')
    asiakas = asiakkaat.query.filter.by(id=currAsiakas).first()
    asiakas.nimi = 'MUOKATTU'
    db.session.commit()
    return jsonify(asiakasdata)

#Asiakkaan, eli käyttäjän poistaminen tietokannasta.

@app.route('/asiakkaat/delete/<id>', methods=['GET', 'POST'])
def deleteAsiakkaat(id):
    asiakasdata = asiakkaat.query.get(id)
    db.session.delete(asiakasdata)
    db.session.commit()
    return jsonify(asiakasdata)

#Työtila-olion luominen tietokantaan.

class tilat(db.Model):
    __tablename__ = 'tyotilat'
    ttNimi = db.Column(db.String(50), primary_key=True)
    ttKuvaus = db.Column(db.String(), nullable=False)
    ttTyyppi = db.Column(db.String(60), nullable=False)

    def __init__(self, ttNimi, ttKuvaus, ttTyyppi):
        self.ttNimi = ttNimi
        self.ttKuvaus = ttKuvaus
        self.ttTyyppi = ttTyyppi

#Tilojen lisääminen tietokantaan.

@app.route('/tilat', methods=['POST'])
def postTilat():
    tiladata = request.get_json()
    tila = tilat(ttNimi=tiladata['ttNimi'], ttKuvaus=tiladata['ttKuvaus'], ttTyyppi=tiladata['ttTyyppi'])
    db.session.add(tila)
    db.session.commit()
    return jsonify(tiladata)

#Tilojen hakeminen tietokannasta.

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

#Route, joka mahdollistaa tilojen Admin-hallinnoinnin, toisin sanoen niiden poistamisen
#tietokannasta kokonaan.

@app.route('/tilat/delete/<ttNimi>', methods=['GET', 'POST', 'DELETE'])
def deleteTilat(ttNimi):
    tiladata = tilat.query.get(ttNimi)
    db.session.delete(tiladata)
    db.session.commit()
    return jsonify(tiladata)

#Määritellään varauksen olio ja minkälaista dataa se pitää sisällään.

class Reservation(db.Model):
    __tablename__ = 'Varaukset'
    id = db.Column(db.Integer, primary_key=True)
    telephone = db.Column(db.String(32))
    date = db.Column(db.DateTime, index=True)

#Tämä route mahdollistaa varausten pyytämisen GET-komennolla tietokannasta.
#Valmiissa UI:ssa html-tiedostoon liitetty tietokannan table näyttäisi varaukset.

@app.route('/varaukset', methods=['GET'])
def getvaraukset():
    kaikkivaraukset = Reservation.query.all()
    output = []
    for varaustiedot in kaikkivaraukset:
        currVaraus = {}
        currVaraus['id'] = varaustiedot.id
        currVaraus['telephone'] = varaustiedot.telephone
        currVaraus['date'] = varaustiedot.date
        output.append(currVaraus)
    return jsonify(output)

#Postman ohjeet: Jsonissa id ILMAN heittomerkkejä, pvm muodossa. 16/Dec/2020 esim.
#Tämä route mahdollistaa varausdatan ajon tietokantantaan.
#UI:n html formi lähettäisit siis POST pyynnön varauksen submit-nappulasta.

@app.route('/varaukset', methods=['POST'])
def postVaraukset():
    varausdata = request.get_json()
    varaus = Reservation(id=varausdata['id'], telephone=varausdata['telephone'], date=varausdata['date'])
    db.session.add(varaus)
    db.session.commit()
    return jsonify(varausdata)

#Route, jonka avulla varauksia voidaan poistaa ladattavasta tietokannasta.
#Logiikka olisi sama UI:n kannalta: Haku ID-numerolla ja poistaminen submitilla.

@app.route('/varaukset/delete/<id>', methods=['GET', 'POST'])
def deleteVaraukset(id):
    varaustiedot = Reservation.query.get(id)
    db.session.delete(varaustiedot)
    db.session.commit()
    return jsonify(varaustiedot)

#Tällä routella pitäisi avautua 404 sivu, ja kuva "I love bugs" näkyä...
#Aloitussivuna tällä hetkellä, koska käyttöliittymän suunnittelu on kesken, eli
#html-formien ja muiden komponenttien relaatiot @app.routeihin.
@app.route('/')
def index():
    return render_template('404.html')



if __name__ == "__main__":
    app.run(port=5000, debug=True)
