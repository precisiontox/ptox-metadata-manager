""" This module contains all queries related to users.
"""

from datetime import datetime
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
    current_user: User = User.query.filter(User.username == username).first()
    if not current_user:
        return jsonify({"msg": "Bad username or password"}), 401
    jti, jwt = current_user.login(password)
    session.add(jti)
    session.commit()
    return jsonify({"access_token": jwt}), 200


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
