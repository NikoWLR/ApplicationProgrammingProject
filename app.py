import os
from flask import Flask, jsonify, request
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Korvaa postgres oman tietokannan nimellä ja admin omalla salasanalla.
# Tämän jälkeen PyCharmin terminalissa komennot: python -> from app import db -> db.create_all()
# Tämän pitäisi luoda tietokanta pgadminiin. Serverin sain itse päälle vaan ajamalla terminalissa komennon: flask run

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost'
api = Api(app)
db = SQLAlchemy(app)


# Users-olion luominen ja siihen tarvittava data.


class Users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    name = db.Column(db.String(32))

    def __init__(self, id, name, email):
        self.id = id
        self.email = email
        self.name = name


# Tämä route hakee KAIKKIEN asiakkaiden tiedot tietokannasta.


@app.route('/users', methods=['GET'])
def getusers():
    allusers = Users.query.all()
    output = []
    for userdata in allusers:
        currUser = {}
        currUser['id'] = userdata.id
        currUser['email'] = userdata.email
        currUser['name'] = userdata.name
        output.append(currUser)
    return jsonify(output)


# Uuden käyttäjän luominen tietokantaan.


@app.route('/users', methods=['POST'])
def postUsers():
    userdata = request.get_json()
    user = Users(id=userdata['id'], email=userdata['email'], name=userdata['name'])
    db.session.add(user)
    db.session.commit()
    return jsonify(userdata)


# Käyttäjän poistaminen tietokannasta. HEITTÄÄ POSTMANISSA ERRORIN, TOIMII SILTI.

@app.route('/users/delete/<id>', methods=['GET', 'POST', 'DELETE'])
def deleteUsers(id):
    userdata = Users.query.get(id)
    db.session.delete(userdata)
    db.session.commit()
    return jsonify(userdata)


# Työtila-olion luominen tietokantaan.

class WorkSpaces(db.Model):
    __tablename__ = 'workspaces'
    workspaceId = db.Column(db.Integer, primary_key=True)
    workspaceName = db.Column(db.String(50), nullable=False)
    workspaceDescription = db.Column(db.String(), nullable=False)

    def __init__(self, workspaceId, workspaceName, workspaceDescription):
        self.workspaceId = workspaceId
        self.workspaceName = workspaceName
        self.workspaceDescription = workspaceDescription


# Tilojen lisääminen tietokantaan.

@app.route('/workspaces', methods=['POST'])
def postWorkspaces():
    workspaceData = request.get_json()
    workspace = WorkSpaces(workspaceId=workspaceData['workspaceId'],
                           workspaceName=workspaceData['workspaceName'],
                           workspaceDescription=workspaceData['workspaceDescription'])
    db.session.add(workspace)
    db.session.commit()
    return jsonify(workspaceData)


# Tilojen hakeminen tietokannasta.

@app.route('/workspaces', methods=['GET'])
def getWorkspaces():
    allWorkspaces = WorkSpaces.query.all()
    output = []
    for workspaces in allWorkspaces:
        currWorkspace = {}
        currWorkspace['workspaceId'] = workspaces.workspaceId
        currWorkspace['workspaceName'] = workspaces.workspaceName
        currWorkspace['workspaceDescription'] = workspaces.workspaceDescription
        output.append(currWorkspace)
    return jsonify(output)


# Route, joka mahdollistaa tilojen  poistamisen tietokannasta.


@app.route('/workspaces/delete/<workspaceId>', methods=['GET', 'POST', 'DELETE'])
def deleteWorkspaces(workspaceId):
    workspaceData = WorkSpaces.query.get(workspaceId)
    db.session.delete(workspaceData)
    db.session.commit()
    return jsonify(workspaceData)


# Määritellään varaus ja sen sisältämä data.

class Reservation(db.Model):
    __tablename__ = 'Reservations'
    id = db.Column(db.Integer, primary_key=True)
    telephone = db.Column(db.String(32))
    date = db.Column(db.DateTime, index=True)


# Tämä route mahdollistaa varausten pyytämisen GET-komennolla tietokannasta.


@app.route('/reservations', methods=['GET'])
def getReservations():
    allReservations = Reservation.query.all()
    output = []
    for reservationData in allReservations:
        currReservation = {}
        currReservation['id'] = reservationData.id
        currReservation['telephone'] = reservationData.telephone
        currReservation['date'] = reservationData.date
        output.append(currReservation)
    return jsonify(output)


# Jsonissa id ILMAN heittomerkkejä ja pvm muodossa. dd/month/yyyy hh:mm esim. 30/Jan/2020 12:45
# Tämä route mahdollistaa varausdatan lisäämisen tietokantantaan.

@app.route('/reservations', methods=['POST'])
def postReservations():
    reservationData = request.get_json()
    newReservation = Reservation(id=reservationData['id'],
                                 telephone=reservationData['telephone'],
                                 date=reservationData['date'])
    db.session.add(newReservation)
    db.session.commit()
    return jsonify(reservationData)


# Route, jonka avulla varauksia voidaan poistaa ladattavasta tietokannasta.


@app.route('/reservations/delete/<id>', methods=['GET', 'POST', 'DELETE'])
def deleteReservations(id):
    reservationData = Reservation.query.get(id)
    db.session.delete(reservationData)
    db.session.commit()
    return jsonify(reservationData)


# Ajaa itse sovelluksen


if __name__ == "__main__":
    app.run(port=5000, debug=True)
