""" Configuration file for Flask and SQLAlchemy. This is where all extensions are initialised and the assembly between
Flask and SQLAlchemy is established. This file also contains the Base variable that is required to establish a
connection to the database and bindings to the JWT managers, the CORS managers and, later, the session manager
# TODO: add session manager from flask-session

:author: D. Batista (Terazus)
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy, Model
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger

from .const import SQLALCHEMY_SECRET_KEY

db: SQLAlchemy = SQLAlchemy()
app: Flask = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = SQLALCHEMY_SECRET_KEY
jwt: JWTManager = JWTManager(app)
CORS(app)
Base: Model = db.Model
swagger: Swagger = Swagger(app)
