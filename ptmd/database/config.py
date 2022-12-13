from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from .const import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_SECRET_KEY

db = SQLAlchemy()
app = Flask(__name__)
app.config.from_object(__name__)
# app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SQLALCHEMY_SECRET_KEY
jwt = JWTManager(app)
CORS(app)
Base = db.Model
Table = db.Table


