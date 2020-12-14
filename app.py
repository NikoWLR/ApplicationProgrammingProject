from flask import Flask, jsonify, request
from flask_restful import Api
from http import HTTPStatus

app = Flask(__name__)
api = Api(app)

if __name__ == "__main__":
    app.run(port=5000, debug=True)