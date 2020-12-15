from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
db = SQLAlchemy(app)


# "Jos varattu = true -> heitä error message x . "
# Työtilat" table, jossa toistaiseksi vain työtilan nimi ja kuvaus."
# Myöhemmin mahdollisesti myös boolean arvolla toimiva "varattu" rivi.
class tilat (db.Model):
    __tablename__ = 'tyotilat'
    ttNimi = db.Column(db.String(50), primary_key = True)
    ttKuvaus = db.Column(db.String(), nullable = False)
    #ttTyyppi = db.Column(db.String(60), nullable=False)

    def __init__(self, ttNimi, ttKuvaus, ttTyyppi):
        self.ttNimi = ttNimi
        self.ttKuvaus = ttKuvaus
        self.ttTyyppi = ttTyyppi

# "Asiakkaat-table" jossa:
class asiakkaat (db.Model):
    __tablename__ = 'asiakkaat'
    AsiakasNimi = db.Column(db.String(50), primary_key = True)
    AsiakasEmail = db.Column(db.String(), nullable = False)

    def __init__(self, asiakasNimi, asiakasEmail):
        self.asiakasNimi = asiakasNimi
        self.asiakasEmail = asiakasEmail



