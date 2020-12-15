from flask import Flask, jsonify, request
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

# from database import tilat


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost'
api = Api(app)
db = SQLAlchemy(app)


# "Työtilat" table, jossa toistaiseksi vain työtilan nimi ja kuvaus.
# Myöhemmin mahdollisesti myös boolean arvolla toimiva "varattu" rivi. Jos varattu = true -> heitä error message x .

class tilat(db.Model):
    __tablename__ = 'tyotilat'
    ttNimi = db.Column(db.String(50), primary_key=True)
    ttKuvaus = db.Column(db.String(), nullable=False)
    ttTyyppi = db.Column(db.String(60), nullable=False)

    def __init__(self, ttNimi, ttKuvaus, ttTyyppi):
        self.ttNimi = ttNimi
        self.ttKuvaus = ttKuvaus
        self.ttTyyppi = ttTyyppi


# "Asiakkaat" -table jossa asiakkaan nimi ja sähköposti
class asiakkaat(db.Model):
    __tablename__ = 'asiakkaat'
    AsiakasNimi = db.Column(db.String(50), primary_key=True)
    AsiakasEmail = db.Column(db.String(), nullable=False)

    def __init__(self, asiakasNimi, asiakasEmail):
        self.asiakasNimi = asiakasNimi
        self.asiakasEmail = asiakasEmail


@app.route('/test', methods=['GET'])
def test():
    return {
        'test': 'test1'
    }


# @app.route('/asiakkaat', methods =['GET'])
# def gasiakkaat():
#    kaikkiAsiakkaat = asiakkaat.query.all()
#    output = []
#    for asiakkaat in kaikkiAsiakkaat:
#        currAsiakas = {}
#        currAsiakas ['AsiakasNimi']= asiakkaat.AsiakasNimi
#        currAsiakas ['AsiakasEmail']= asiakkaat.AsiakasEmail
#        output.append (currAsiakas)
#    return jsonify(output)

@app.route('/tilat', methods=['GET'])
def gettilat():
    kaikkitilat = tilat.query.all()
    output = []
    for tyotilat in kaikkitilat:
        currTila = {}
        currTila['ttNimi'] = tyotilat.ttNimi
        currTila['ttKuvaus'] = tyotilat.ttKuvaus
        currTila['ttTyyppi'] = tyotilat.ttTyyppi
        output.append(currTila)
    return jsonify(output)


@app.route('/tilat', methods=['POST'])
def posttilat():
    tiladata = request.get_json()
    tila = tilat(ttNimi=tiladata['ttNimi'], ttKuvaus=tiladata['ttKuvaus'], ttTyyppi=tiladata['ttTyyppi'])
    db.session.add(tila)
    db.session.commit()
    return jsonify(tiladata)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
