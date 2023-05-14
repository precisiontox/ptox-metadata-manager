""" This module contains the API routes

@author: D. Batista (Terazus)
"""
from os import path

from flask import Response
from flask_jwt_extended import jwt_required
from flasgger import swag_from  # type: ignore

from ptmd.config import app
from ptmd.api.queries import (
    login as login_user, change_password, get_me, logout, enable_account, validate_account,
    get_organisms, get_organisations,
    get_chemicals, create_chemicals,
    create_gdrive_file, create_user, validate_file,  register_gdrive_file
)
from ptmd.api.const import SWAGGER_DATA_PATH, FILES_DOC_PATH, USERS_DOC_PATH, CHEMICALS_DOC_PATH


###########################################################
#                   USERS ROUTES                          #
###########################################################
@app.route('/api/users', methods=['PUT'])
@swag_from(path.join(USERS_DOC_PATH, 'change_password.yml'))
@jwt_required()
def change_pwd() -> tuple[Response, int]:
    """ Change the password of the current user """
    return change_password()


@app.route('/api/users', methods=['POST'])
@swag_from(path.join(USERS_DOC_PATH, 'create_user.yml'))
def user() -> tuple[Response, int]:
    """ Create a new user """
    return create_user()


@app.route("/api/users", methods=["GET"])
@swag_from(path.join(USERS_DOC_PATH, 'me.yml'))
@jwt_required()
def me() -> tuple[Response, int]:
    """ Get the current user"""
    return get_me()


@app.route("/api/session", methods=["POST"])
@swag_from(path.join(USERS_DOC_PATH, 'login.yml'))
def login() -> tuple[Response, int]:
    """ Route to log in a user """
    return login_user()


@app.route("/api/session", methods=["DELETE"])
@swag_from(path.join(USERS_DOC_PATH, 'logout.yml'))
@jwt_required()
def modify_token() -> tuple[Response, int]:
    """ Route to log out a user """
    return logout()


@app.route("/api/users/enable/<token>", methods=["GET"])
@swag_from(path.join(USERS_DOC_PATH, 'enable_account.yml'))
def enable_account_(token: str) -> tuple[Response, int]:
    """ Route to enable a user account

    :param token: the token sent by email that will enable the account
    """
    return enable_account(token)


@app.route("/api/users/<user_id>/activate", methods=["GET"])
@swag_from(path.join(USERS_DOC_PATH, 'validate_account.yml'))
def validate_account_(user_id: int) -> tuple[Response, int]:
    """ Route to validate a user account. This is an admin only route

    :param user_id: the id of the user to validate
    """
    return validate_account(user_id)


###########################################################
#                     CHEMICALS                           #
###########################################################
@app.route('/api/chemicals', methods=['GET'])
@swag_from(path.join(CHEMICALS_DOC_PATH, 'get_chemicals.yml'))
@jwt_required()
def chemicals() -> tuple[Response, int]:
    """ Get the list of chemicals """
    return get_chemicals()


@app.route('/api/chemicals', methods=['POST'])
@swag_from(path.join(CHEMICALS_DOC_PATH, 'create_chemicals.yml'))
@jwt_required()
def new_chemicals() -> tuple[Response, int]:
    """ Create a new chemical """
    return create_chemicals()


###########################################################
#                   MISCELLANEOUS                         #
###########################################################
@app.route('/api/organisms', methods=['GET'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'organisms.yml'))
@jwt_required()
def organisms() -> tuple[Response, int]:
    """ Get the list of organisms """
    return get_organisms()


@app.route('/api/organisations', methods=['GET'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'organisations.yml'))
@jwt_required()
def organisations() -> tuple[Response, int]:
    """ Get the list of organisations """
    return get_organisations()


###########################################################
#                          FILES                          #
###########################################################
@app.route('/api/files', methods=['POST'])
@swag_from(path.join(FILES_DOC_PATH, 'create_file.yml'))
@jwt_required()
def create_file() -> tuple[Response, int]:
    """ Create and saves the spreadsheet in the Google Drive """
    return create_gdrive_file()


@app.route('/api/files/<file_id>/validate', methods=['GET'])
@swag_from(path.join(FILES_DOC_PATH, 'validate_file.yml'))
@jwt_required()
def validate(file_id: int) -> tuple[Response, int]:
    """ Validate a file

    :param file_id: the id of the file to validate
    """
    return validate_file(file_id)


@app.route('/api/files/register', methods=['POST'])
@swag_from(path.join(FILES_DOC_PATH, 'register_file.yml'))
@jwt_required()
def register_file() -> tuple[Response, int]:
    """ Register a file from an external Google Drive """
    return register_gdrive_file()
