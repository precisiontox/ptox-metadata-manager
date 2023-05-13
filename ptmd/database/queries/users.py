""" This module contains all queries related to users.

@author: D. Batista (Terazus)
"""

from datetime import timedelta
from flask_jwt_extended import create_access_token
from flask import jsonify, Response

from ptmd.config import session
from ptmd.logger import LOGGER
from ptmd.database.models import User


def login_user(username: str, password: str) -> tuple[Response, int]:
    """ Login a user and return a JWT token. The username and password are retrieved from the request body.

    @param username
    @param password
    @return: Response, int: the response message and the response code
    """
    raw_user = User.query.filter(User.username == username).first()
    user = dict(raw_user) if raw_user and raw_user.validate_password(password) else None
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=user['id'], expires_delta=timedelta(days=1000000))
    return jsonify(access_token=access_token), 200


def create_users(users: list[dict]) -> dict[int, User]:
    """ Create users in the database.

    :param users: list[dict]: list of users
    :return: bool: True if the users were created, False otherwise
    """
    LOGGER.info('Creating users')
    created_users = {}
    for user_index, user in enumerate(users):
        session.add(User(**user))
        user_from_db = User.query.filter(User.username == user['username']).first()
        created_users[user_index] = user_from_db
    session.commit()
    return created_users
