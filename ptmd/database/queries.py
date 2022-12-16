""" This module contains the database models and a function to login users. This may need to be split into a proper
module later on.

:author: D. Batista (Terazus)
"""

from datetime import timedelta

from flask_jwt_extended import create_access_token
from flask import jsonify, Response
from sqlalchemy.orm import session as sqlsession

from ptmd.database.utils import get_session
from ptmd.database.models.user import User
from ptmd.database.models.chemical import Chemical


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


def get_allowed_chemicals() -> list[str]:
    """ Get the list of allowed chemicals names.
    """
    session = get_session()
    allowed_chemicals = [chemical.common_name for chemical in session.query(Chemical).all()]
    session.close()
    return allowed_chemicals
