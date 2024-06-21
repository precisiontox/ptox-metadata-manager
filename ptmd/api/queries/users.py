""" This module contains the functions to handle the queries related to users:
- login
- change password
- get the current user
- create a new user
"""
from json import loads

from flask import jsonify, request, Response
from flask_jwt_extended import get_jwt, get_current_user
from sqlalchemy.exc import IntegrityError
from jsonschema import Draft4Validator as Validator

from ptmd.logger import LOGGER
from ptmd.config import session
from ptmd.const import CREATE_USER_SCHEMA_PATH
from ptmd.database import login_user, get_token, User, Token, Organisation
from ptmd.exceptions import PasswordPolicyError, TokenInvalidError, TokenExpiredError, InvalidPasswordError
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
        organisation: Organisation = Organisation.query.filter(
            Organisation.name == user_data['organisation']
        ).first().organisation_id
        del user_data['organisation']
        user: User = User(**user_data, organisation_id=organisation)
        session.add(user)
        session.commit()
        user_dict = dict(user)
        return jsonify(user_dict), 200
    except IntegrityError:
        return jsonify({"msg": "Username or email already taken"}), 400
    except PasswordPolicyError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception:
        return jsonify({"msg": "An unexpected error occurred"}), 500


def login() -> tuple[Response, int]:
    """ Function to log in a user. Acquire data from a JSON request

    :return: tuple containing a JSON response and a status code
    """
    username: str = request.json.get('username', None)
    password: str = request.json.get('password', None)
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    try:
        return login_user(username=username, password=password)
    except InvalidPasswordError as e:
        return jsonify({"msg": str(e)}), 401
    except Exception:
        return jsonify({"msg": "An unexpected error occurred"}), 500


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

    if password == new_password:
        return jsonify({"msg": "New password cannot be the same as the old one"}), 400

    user: User = User.query.filter(User.id == get_jwt()['sub']).first()
    try:
        changed: bool = user.change_password(old_password=password, new_password=new_password)
        if not changed:
            return jsonify({"msg": "Wrong password"}), 400
        return jsonify({"msg": "Password changed successfully"}), 200 if changed else jsonify()
    except PasswordPolicyError as e:
        return jsonify({"msg": str(e)}), 400
    except Exception:
        return jsonify({"msg": "An unexpected error occurred"}), 500


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
    current_user: User = get_current_user()
    current_user.revoke_jwts()
    session.commit()
    return jsonify(msg="Logout successfully"), 200


@check_role(role='admin')
def validate_account(user_id: int) -> tuple[Response, int]:
    """ Validates the account of a user. Admin only

    :param user_id: ID of the user to validate
    :return: tuple containing a JSON response and a status code
    """
    user: User = User.query.filter(User.id == user_id).first()
    user.set_role('user')
    return jsonify(msg="Account validated"), 200


def enable_account(token: str) -> tuple[Response, int]:
    """ Enables the account of a user by a link sent by email

    :param token: token to enable the account
    :return: tuple containing a JSON response and a status code
    """
    try:
        token_from_db: Token = get_token(token=token)
        user: User = token_from_db.user_activation[0]
        user.set_role('enabled')
        return jsonify(msg="Account enabled. An email has been to an admin to validate your account."), 200
    except Exception as e:
        LOGGER.error("Account not enabled: %s", e)
        return jsonify(msg='Failed to enable your account. Please contact an admin for assistance.'), 400


@check_role(role='admin')
def get_users() -> tuple[Response, int]:
    """ Gets all the users in the database. Admin only

    :return: tuple containing a JSON response and a status code
    """
    users: list[User] = User.query.all()
    users_dict: list[dict] = []
    for user in users:
        users_dict.append({
            'id': user.id,
            'username': user.username,
            'organisation': user.organisation.name if user.organisation else None,
            'role': user.role,
            'email': user.email,
            'files': [file.file_id for file in user.files]
        })
    return jsonify(users_dict), 200


def send_reset_email() -> tuple[Response, int]:
    """ Sends an email to the user to reset his password

    :return: tuple containing a JSON response and a status code
    """
    response: tuple[Response, int] = jsonify({"msg": "Email sent"}), 200
    email: str = request.json.get('email', None)
    if not email:
        return jsonify({"msg": "Missing email"}), 400
    user: User = User.query.filter(User.email == email).first()
    if user is None:
        return response

    reset_token: Token = user.reset_token
    if reset_token:
        session.delete(reset_token)  # type: ignore
    reset_token = Token(user=user, token_type='reset')
    session.add(reset_token)
    user.reset_token = reset_token
    session.add(user)
    session.commit()
    return response


def reset_password(token: str) -> tuple[Response, int]:
    """ Resets the password of a user

    :param token: the token to reset the password
    :return: tuple containing a JSON response and a status code
    """
    password: str = request.json.get('password', None)
    if not password:
        return jsonify({"msg": "Missing password"}), 400
    try:
        reset_token_from_db: Token = get_token(token=token)
        user: User = reset_token_from_db.user_reset[0]
        user.set_password(password)
        session.delete(reset_token_from_db)  # type: ignore
        session.commit()
        return jsonify({"msg": "Password changed successfully"}), 200
    except (PasswordPolicyError, TokenInvalidError, TokenExpiredError) as e:
        return jsonify({"msg": str(e)}), 400
    except Exception:
        return jsonify({"msg": "An unexpected error occurred"}), 500


@check_role(role='admin')
def change_role(user_id: int, role: str) -> tuple[Response, int]:
    """ Change the role of a user. Admin only

    :param user_id: ID of the user to make admin
    :param role: role to change to
    :return: tuple containing a JSON response and a status code
    """
    user: User = User.query.filter(User.id == user_id).first()
    if not user:
        return jsonify(msg="User not found"), 404
    current_user: User = get_current_user()
    if current_user.id == user.id:
        return jsonify(msg="Cannot change your own role"), 400
    try:
        user.set_role(role)
        return jsonify(msg=f"User {user_id} role has been changed to {role}"), 200
    except ValueError:
        return jsonify(msg="Invalid role"), 400


def delete_user(user_id: int) -> tuple[Response, int]:
    """ Delete a user. Admin or self only

    :param user_id: ID of the user to delete
    :return: tuple containing a JSON response and a status code
    """
    current_user: User = get_current_user()
    user: User = User.query.filter(User.id == user_id).first()
    if not user:
        return jsonify(msg="User not found"), 404
    if user.id == 1:
        return jsonify(msg="Cannot delete super user"), 400
    if current_user.role != 'admin' and user.id != current_user.id:
        return jsonify(msg="Unauthorized"), 401
    admin: User = User.query.filter(User.id == 1).first()
    for file in user.files:
        file.author = admin
    session.delete(user)  # type: ignore
    session.commit()
    return jsonify(msg=f"User {user_id} deleted"), 200


def verify_token() -> tuple[Response, int]:
    """ Verify if the token is valid

    :return: tuple containing a JSON response and a status code
    """
    return jsonify(True), 200
