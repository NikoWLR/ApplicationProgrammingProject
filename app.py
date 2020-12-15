import os
from flask import Flask, jsonify, request, abort, g, url_for, make_response
from flask_restful import Api
from http import HTTPStatus
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from datetime import datetime
from flask_mail import Mail, Message

#Flask serverin sekä Databasen määritys eli conffaus.

app = Flask(__name__)
app.config['SECRET_KEY'] = 'haluttu salaus avain'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
#api = Api(app)

#Sähköpostifunktion määrittäminen

app.config.update(
    DEBUG=True,
    #EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = '<email to be used to send emails>',
    MAIL_PASSWORD = '<app password>'
    )

db = SQLAlchemy(app)
auth = HTTPBasicAuth()
mail = Mail(app)

if __name__ == "__main__":
    if not os.path.exists(Nikon database):
    app.run(port=5000, debug=True)