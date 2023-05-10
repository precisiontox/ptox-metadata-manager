""" This module contains the API routes

@author: D. Batista (Terazus)
"""
from os import path

from flask_jwt_extended import jwt_required
from flasgger import swag_from

from ptmd.config import app
from ptmd.const import ROOT_PATH
from ptmd.api.queries import (
    login as login_user, change_password, get_me, logout,
    get_organisms, get_chemicals, get_organisations,
    create_gdrive_file, create_user, validate_file,  register_gdrive_file
)


SWAGGER_DATA_PATH: str = path.join(ROOT_PATH, 'resources', 'api')
FILES_DOC_PATH: str = path.join(SWAGGER_DATA_PATH, 'files')
USERS_DOC_PATH: str = path.join(SWAGGER_DATA_PATH, 'users')


###########################################################
#                   USERS ROUTES                          #
###########################################################
@app.route('/api/users', methods=['PUT'])
@swag_from(path.join(USERS_DOC_PATH, 'change_password.yml'))
@jwt_required()
def change_pwd():
    """ Change the password of the current user """
    return change_password()


@app.route('/api/users', methods=['POST'])
@swag_from(path.join(USERS_DOC_PATH, 'create_user.yml'))
@jwt_required()
def user():
    """ Create a new user """
    return create_user()


@app.route("/api/users", methods=["GET"])
@swag_from(path.join(USERS_DOC_PATH, 'me.yml'))
@jwt_required()
def me():
    """ Get the current user"""
    return get_me()


@app.route("/api/session", methods=["POST"])
@swag_from(path.join(USERS_DOC_PATH, 'login.yml'))
def login():
    """ Route to log in a user """
    return login_user()


@app.route("/api/session", methods=["DELETE"])
@swag_from(path.join(USERS_DOC_PATH, 'logout.yml'))
@jwt_required()
def modify_token():
    """ Route to log out a user """
    return logout()


###########################################################
#                   MISCELLANEOUS                         #
###########################################################

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


###########################################################
#                   ORGANISATIONS                         #
###########################################################

@app.route('/api/organisations', methods=['GET'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'organisations.yml'))
@jwt_required()
def organisations():
    """ Get the list of organisations """
    return get_organisations()


###########################################################
#                          FILES                          #
###########################################################

@app.route('/api/files', methods=['POST'])
@swag_from(path.join(FILES_DOC_PATH, 'create_file.yml'))
@jwt_required()
def create_file():
    """ Create and saves the spreadsheet in the Google Drive """
    return create_gdrive_file()


@app.route('/api/files/<file_id>/validate', methods=['GET'])
@swag_from(path.join(FILES_DOC_PATH, 'validate_file.yml'))
@jwt_required()
def validate(file_id: int):
    """ Validate a file """
    return validate_file(file_id)


@app.route('/api/files/register', methods=['POST'])
@swag_from(path.join(FILES_DOC_PATH, 'register_file.yml'))
@jwt_required()
def register_file():
    """ Register a file from an external Google Drive """
    return register_gdrive_file()
