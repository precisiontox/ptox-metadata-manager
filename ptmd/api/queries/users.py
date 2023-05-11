""" This module contains the functions to handle the queries related to users:
- login
- change password
- get the current user
- create a new user

@author: D. Batista (Terazus)
"""

from datetime import datetime, timezone
from json import loads

from flask import jsonify, request, Response
from flask_jwt_extended import get_jwt
from sqlalchemy.exc import IntegrityError
from jsonschema import Draft202012Validator as Validator

from ptmd.config import session
from ptmd.const import CREATE_USER_SCHEMA_PATH
from ptmd.database import login_user, User, TokenBlocklist, Token
from .utils import check_role


def create_user() -> tuple[Response, int]:
    """ Create a new user

    :return: tuple containing a JSON response and a status code
    """
    user_data: dict = request.json
    with open(CREATE_USER_SCHEMA_PATH, 'r') as f:
        schema: dict = loads(f.read())
    validator: Validator = Validator(schema)
    for error in validator.iter_errors(user_data):
        return jsonify({"msg": {'field': error.path[0], 'error': error.message}}), 400

    if user_data['password'] != user_data['confirm_password']:
        return jsonify({"msg": "Passwords do not match"}), 400

    try:
        del user_data['confirm_password']
        user: User = User(**user_data)
        session.add(user)
        session.commit()
        user_dict = dict(user)
        return jsonify(user_dict), 200
    except IntegrityError:
        return jsonify({"msg": "Username already taken"}), 400


def login() -> tuple[Response, int]:
    """ Function to log in a user. Acquire data from a JSON request

    :return: tuple containing a JSON response and a status code
    """
    username: str = request.json.get('username', None)
    password: str = request.json.get('password', None)
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    logged_in: tuple[Response, int] = login_user(username=username, password=password)
    return logged_in


@check_role(role='disabled')
def change_password() -> tuple[Response, int]:
    """ Function to change the password of the current user. Acquire data from a JSON request.

    :return: tuple containing a JSON response and a status code
    """

    password: str = request.json.get('old_password', None)
    new_password: str = request.json.get('new_password', None)
    repeat_password: str = request.json.get('confirm_password', None)

    if not new_password or not repeat_password:
        return jsonify({"msg": "Missing new_password or confirm_password"}), 400
    if new_password != repeat_password:
        return jsonify({"msg": "Passwords do not match"}), 400

    user: User = User.query.filter(User.id == get_jwt()['sub']).first()
    changed: bool = user.change_password(old_password=password, new_password=new_password)
    if not changed:
        return jsonify({"msg": "Wrong password"}), 400
    return jsonify({"msg": "Password changed successfully"}), 200


@check_role(role='disabled')
def get_me() -> tuple[Response, int]:
    """ Function to get the current user. Acquire data from the JWT

    :return: tuple containing a JSON response and a status code
    """
    user: dict = dict(User.query.filter(User.id == get_jwt()['sub']).first())
    return jsonify(user), 200


@check_role(role='disabled')
def logout() -> tuple[Response, int]:
    """ Logs the user out by expiring the token
    """
    session.add(TokenBlocklist(jti=get_jwt()["jti"], created_at=datetime.now(timezone.utc)))
    session.commit()
    return jsonify(msg="Logout successfully"), 200


@check_role(role='admin')
def validate_account(user_id: int) -> tuple[Response, int]:
    user: User = User.query.filter(User.id == user_id).first()
    user.activate_account()
    return jsonify(msg="Account validated"), 200


def enable_account(token: str) -> tuple[Response, int]:
    token: Token = Token.query.filter(Token.token == token).first()
    if token is None:
        return jsonify(msg="Invalid token"), 400
    if token.expires_on < datetime.now(token.expires_on.tzinfo):
        return jsonify(msg="Token expired"), 400
    user: User = token.user[0]
    user.enable_account()
    return jsonify(msg="Account enabled. An email has been to an admin to validate your account."), 200
