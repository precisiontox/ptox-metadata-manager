""" This module contains the API routes

@author: D. Batista (Terazus)
"""
from os import path

from flask_jwt_extended import jwt_required
from flasgger import swag_from

from ptmd.database import app
from ptmd.const import ROOT_PATH
from .queries import (
    login as login_user, change_password,
    get_me, get_organisms, get_chemicals, get_organisations,
    create_gdrive_file,
    create_user,
    validate_file
)


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


@app.route('/api/organisms', methods=['GET'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'organisms.yml'))
@jwt_required()
def organisms():
    """ Get the list of organisms """
    return get_organisms()


@app.route('/api/chemicals', methods=['GET'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'chemicals.yml'))
@jwt_required()
def chemicals():
    """ Get the list of chemicals """
    return get_chemicals()


@app.route('/api/organisations', methods=['GET'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'organisations.yml'))
@jwt_required()
def organisations():
    """ Get the list of organisations """
    return get_organisations()


@app.route('/api/change_password', methods=['POST'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'change_password.yml'))
@jwt_required()
def change_pwd():
    """ Change the password of the current user """
    return change_password()


@app.route('/api/user', methods=['POST'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'create_user.yml'))
@jwt_required()
def user():
    """ Create a new user """
    return create_user()


@app.route('/api/file/<file_id>/validate', methods=['GET'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'validate_file.yml'))
@jwt_required()
def validate(file_id: int):
    """ Validate a file """
    return validate_file(file_id)
