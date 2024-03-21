""" This module contains all queries related to users.
"""

from datetime import timedelta, datetime
from flask_jwt_extended import create_access_token
from flask import jsonify, Response

from ptmd.config import session
from ptmd.logger import LOGGER
from ptmd.exceptions import TokenExpiredError, TokenInvalidError
from ptmd.database.models import User, Token


def login_user(username: str, password: str) -> tuple[Response, int]:
    """ Login a user and return a JWT token. The username and password are retrieved from the request body.

    :param username
    :param password
    :return: Response, int: the response message and the response code
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


def get_token(token: str) -> Token:
    """ Gets a token from the database and checks if it is valid

    :param token: the token to get
    :return: the token from the database

    :raises Exception: if the token is invalid
    :raises Exception: if the token is expired
    """
    token_from_db: Token = Token.query.filter(Token.token == token).first()
    if token_from_db is None:
        raise TokenInvalidError
    if token_from_db.expires_on < datetime.now(token_from_db.expires_on.tzinfo):
        session.delete(token_from_db)  # type: ignore
        session.commit()
        raise TokenExpiredError
    return token_from_db
