""" This module contains the functions triggered by the API endpoints.
It includes:
    - login_user to log in a user
    - get_me to get the current user
    - create_gdrive_file to create a file in the Google Drive using the data provided by the user
    - get_organisms to get the organisms from the database
    - get_chemicals to get the chemicals from the database
    - change_password to change the password of the current user

@author: D. Batista (Terazus)
"""
from flask import jsonify, request, Response
from flask_jwt_extended import get_jwt
from sqlalchemy.orm import Session

from ptmd.utils import get_session
from ptmd.database import login_user, User, Organism, Chemical
from .create_gdrive_file import CreateGDriveFile


def login() -> tuple[Response, int]:
    """ Function to log in a user. Acquire data from a JSON request

    :return: tuple containing a JSON response and a status code
    """
    session: Session = get_session()
    username: str = request.json.get('username', None)
    password: str = request.json.get('password', None)
    if not username or not password:
        session.close()
        return jsonify({"msg": "Missing username or password"}), 400
    logged_in: tuple[Response, int] = login_user(username=username, password=password, session=session)
    session.close()
    return logged_in


def get_me() -> tuple[Response, int]:
    """ Function to get the current user. Acquire data from the JWT

    :return: tuple containing a JSON response and a status code
    """
    try:
        session: Session = get_session()
        user: User = session.query(User).filter_by(id=get_jwt()['sub']).first()
        session.close()
        return jsonify(dict(user)), 200
    except Exception:
        return jsonify({"msg": "Invalid token"}), 401


def create_gdrive_file() -> tuple[Response, int]:
    """ Function to create a file in the Google Drive using the data provided by the user. Acquire data from a
    JSON request.

    :return: tuple containing a JSON response and a status code
    """
    try:
        payload: CreateGDriveFile = CreateGDriveFile()
        session: Session = get_session()
        response: dict[str, str] = payload.process_file(session=session)
        session.close()
        return jsonify({"data": {'file_url': response['alternateLink']}}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


def get_organisms() -> tuple[Response, int]:
    """ Function to get the organisms from the database.

    :return: tuple containing a JSON response and a status code
    """
    session: Session = get_session()
    organisms: dict[str, list[dict[str, int or str]]] = {
        "data": [dict(organism) for organism in session.query(Organism).all()]
    }
    session.close()
    return jsonify(organisms), 200


def get_chemicals() -> tuple[Response, int]:
    """ Function to get the chemicals from the database.

    :return: tuple containing a JSON response and a status code
    """
    session: Session = get_session()
    response: list[Chemical] = session.query(Chemical).filter(Chemical.ptx_code < 998).all()
    chemicals: dict[str, list[dict[str, int or str]]] = {"data": [dict(chemical) for chemical in response]}
    session.close()
    return jsonify(chemicals), 200


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
