from app import jsonify
from app import db


# "Työtilat" table, jossa toistaiseksi vain työtilan nimi ja kuvaus

class tyotilat (db.Model):
    __tablename__ = 'tyotilat'
    ttNimi = db.Column(db.String(50), primary_key = True)
    ttKuvaus = db.Column(db.String(), nullable = False)

    def __init__(self, ttNimi, ttKuvaus):
        self.ttNimi = ttNimi
        self.ttKuvaus = ttKuvaus

@app.route('/tilat', methods =['GET'])
def gettilat():
    kaikkitilat = tyotilat.query.all()
    output = []
    for tyotilat in kaikkitilat:
        currTila = {}
        currTila ['ttNimi']= tyotilat.ttNimi
        currTila ['ttKuvaus']= tyotilat.ttKuvaus
        output.append (currTila)
    return jsonify(output)

