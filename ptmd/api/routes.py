""" This module contains the API routes

@author: D. Batista (Terazus)
"""
from os import path

from flask import Response
from flask_jwt_extended import jwt_required
from flasgger import swag_from

from ptmd.config import app
from ptmd.api.queries import (
    login as login_user, change_password, get_me, logout, enable_account, validate_account, get_users,
    get_organisms, get_organisations,
    get_chemicals, create_chemicals, get_chemical,
    create_gdrive_file, create_user, validate_file,  register_gdrive_file, search_files_in_database, delete_file,
    get_sample, get_samples,
    ship_data, receive_data,
    convert_to_isa
)
from ptmd.api.const import SWAGGER_DATA_PATH, FILES_DOC_PATH, USERS_DOC_PATH, CHEMICALS_DOC_PATH, SAMPLES_DOC_PATH


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


@app.route("/api/user", methods=["GET"])
@swag_from(path.join(USERS_DOC_PATH, 'me.yml'))
@jwt_required()
def me() -> tuple[Response, int]:
    """ Get the current user"""
    return get_me()


@app.route("/api/users", methods=["GET"])
@swag_from(path.join(USERS_DOC_PATH, 'users.yml'))
@jwt_required()
def users() -> tuple[Response, int]:
    """ Get the current user"""
    return get_users()


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


@app.route('/api/chemicals/<ptx_code>', methods=['GET'])
@swag_from(path.join(CHEMICALS_DOC_PATH, 'get_chemical.yml'))
@jwt_required(optional=True)
def chemical(ptx_code: str) -> tuple[Response, int]:
    """ Get a chemical by its PTX code

    :param ptx_code: the PTX code of the chemical
    :return: the chemical and the status code
    """
    return get_chemical(ptx_code)


###########################################################
#                   MISCELLANEOUS                         #
###########################################################
@app.route('/api/organisms', methods=['GET'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'organisms.yml'))
@jwt_required(optional=True)
def organisms() -> tuple[Response, int]:
    """ Get the list of organisms """
    return get_organisms()


@app.route('/api/organisations', methods=['GET'])
@swag_from(path.join(SWAGGER_DATA_PATH, 'organisations.yml'))
@jwt_required(optional=True)
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


@app.route('/api/files/search', methods=['GET'])
@jwt_required()
def search_files() -> tuple[Response, int]:
    """ Search files """
    return search_files_in_database()


@app.route('/api/files/<file_id>', methods=['DELETE'])
@swag_from(path.join(FILES_DOC_PATH, 'delete_file.yml'))
@jwt_required()
def delete_file_(file_id: int) -> tuple[Response, int]:
    """ Delete the given  file

    :param file_id: the id of the file to validate
    """
    return delete_file(file_id)


@app.route('/api/files/<file_id>/ship', methods=['GET'])
@swag_from(path.join(FILES_DOC_PATH, 'ship_file.yml'))
@jwt_required()
def ship_file(file_id: int) -> tuple[Response, int]:
    """ Ship the given file

    :param file_id: the id of the file to ship
    """
    return ship_data(file_id)


@app.route('/api/files/<file_id>/receive', methods=['GET'])
@swag_from(path.join(FILES_DOC_PATH, 'receive_file.yml'))
@jwt_required()
def receive_file(file_id: int) -> tuple[Response, int]:
    """ Receive the given file

    :param file_id: the id of the file to receive
    """
    return receive_data(file_id)


@app.route('/api/files/<file_id>/isa', methods=['GET'])
@swag_from(path.join(FILES_DOC_PATH, 'isa.yml'))
@jwt_required()
def file_to_isa(file_id: int) -> tuple[Response, int]:
    """ Convert the given file to ISA-Tab

    :param file_id: the id of the file to convert
    """
    return convert_to_isa(file_id)


###########################################################
#                          SAMPLES                        #
###########################################################
@app.route('/api/samples/<sample_id>', methods=['GET'])
@swag_from(path.join(SAMPLES_DOC_PATH, 'get_sample.yml'))
@jwt_required()
def get_sample_(sample_id: str) -> tuple[Response, int]:
    """ Get a sample by its id

    :param sample_id: the id of the sample to get
    """
    return get_sample(sample_id)


@app.route('/api/samples', methods=['GET'])
@swag_from(path.join(SAMPLES_DOC_PATH, 'get_samples.yml'))
@jwt_required()
def get_samples_() -> tuple[Response, int]:
    """ Get a list of paginated samples
    """
    return get_samples()
