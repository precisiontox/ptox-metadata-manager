""" This module contains the functions to handle the queries related to users:
- login
- change password
- get the current user
- create a new user

@author: D. Batista (Terazus)
"""

from flask import jsonify, request, Response
from flask_jwt_extended import get_jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .utils import validate_inputs, check_admin_only
from ptmd.utils import get_session
from ptmd.database import login_user, User


@check_admin_only()
def create_user() -> tuple[Response, int]:
    """ Create a new user

    :return: tuple containing a JSON response and a status code
    """
    valid: tuple = validate_inputs(inputs=['username', 'password', 'confirm_password', 'organisation'],
                                   data=request.json)
    if not valid[0]:
        return jsonify({"msg": f"Missing {valid[1]}"}), 400

    user_data = valid[1]
    username: str = user_data['username']
    password: str = user_data['password']
    repeat_password: str = user_data['confirm_password']
    organisation: str = user_data['organisation']

    if password != repeat_password:
        return jsonify({"msg": "Passwords do not match"}), 400

    session: Session = get_session()
    try:
        user: User = User(username=username, password=password, organisation=organisation, session=session)
        session.add(user)
        session.commit()
        user_dict = dict(user)
        session.close()
        return jsonify(dict(user_dict)), 200
    except IntegrityError:
        session.close()
        return jsonify({"msg": "Username already taken"}), 400


def login() -> tuple[Response, int]:
    """ Function to log in a user. Acquire data from a JSON request

    :return: tuple containing a JSON response and a status code
    """
    username: str = request.json.get('username', None)
    password: str = request.json.get('password', None)
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    session: Session = get_session()
    logged_in: tuple[Response, int] = login_user(username=username, password=password, session=session)
    session.close()
    return logged_in


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

    session: Session = get_session()
    user_id: int = get_jwt()['sub']
    user: User = session.query(User).filter_by(id=user_id).first()
    changed: bool = user.change_password(session=session, old_password=password, new_password=new_password)
    session.close()
    if not changed:
        return jsonify({"msg": "Wrong password"}), 400
    return jsonify({"msg": "Password changed successfully"}), 200


def get_me() -> tuple[Response, int]:
    """ Function to get the current user. Acquire data from the JWT

    :return: tuple containing a JSON response and a status code
    """
    session: Session = get_session()
    user: dict = dict(session.query(User).filter_by(id=get_jwt()['sub']).first())
    session.close()
    return jsonify(user), 200
