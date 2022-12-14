""" This module contains the API routes

@author: D. Batista (Terazus)
"""
from os import path

from flask_jwt_extended import jwt_required
from flasgger import swag_from

from ptmd.database import app
from ptmd.const import ROOT_PATH
from .queries import login as login_user, get_me, create_gdrive_file


SWAGGER_DATA_PATH = path.join(ROOT_PATH, 'resources', 'api')


@app.route("/api/login", methods=["POST"])
@swag_from(path.join(SWAGGER_DATA_PATH, 'login.yml'))
def login():
    """ Route to log in a user. Acquire data from a JSON request """
    return login_user()


@app.route("/api/me", methods=["GET"])
@swag_from(path.join(SWAGGER_DATA_PATH, 'me.yml'))
@jwt_required()
def me():
    """ Get the current user"""
    return get_me()


@app.route('/api/create_file', methods=['POST'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'create_file.yml'))
@jwt_required()
def create_file():
    """ Create and saves the spreadsheet in the Google Drive """
    return create_gdrive_file()
