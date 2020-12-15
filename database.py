from flask import request
from flask_restful import Resource
from http import HTTPStatus
import psycopg2
from psycopg2 import Error

#Connect to DB (pyörii itsellä Dockerissa atm, pitää kehitellä joku järkevämpi jossain kohtaa jos ehtii)

con = psycopg2.connect(
            host ="localmachine",
            database ="AppProDB",
            user = "postgres",
            password = "postgres"
            
)
