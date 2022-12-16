""" This module contains the database models and a function to login users. This may need to be split into a proper
module later on.

:author: D. Batista (Terazus)
"""

from datetime import timedelta

from flask_jwt_extended import create_access_token
from flask import jsonify, Response
from sqlalchemy.orm import session as sqlsession

from .user import User
from .chemical import Chemical


def login_user(username: str, password: str, session: sqlsession) -> tuple[Response, int]:
    """ Login a user and return a JWT token. The username and password are retrieved from the request body.

    @param username
    @param password
    @param session: the database session
    @return: Response, int: the response message and the response code
    """
    user = session.query(User).filter_by(username=username).first()
    user = dict(user) if user and user.validate_password(password) else None
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=user['id'], expires_delta=timedelta(days=1000000))
    return jsonify(access_token=access_token), 200


def chemicals_exist(chemicals: list[str], session: sqlsession) -> bool:
    """ Check if a list of chemicals exists in the database.

    @param chemicals: list of chemicals
    @param session: the database session
    @return: bool: True if all chemicals exist, False otherwise
    """
    return all(session.query(Chemical).filter_by(common_name=chemical).first() for chemical in chemicals)
