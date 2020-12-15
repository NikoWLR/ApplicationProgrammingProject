from flask import Flask, jsonify, request
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from database import tilat, asiakkaat


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost'
api = Api(app)
db = SQLAlchemy(app)

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