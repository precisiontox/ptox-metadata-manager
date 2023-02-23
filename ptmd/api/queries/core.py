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
from flask import jsonify, Response
from flask_jwt_extended import get_jwt
from sqlalchemy.orm import Session

from ptmd.utils import get_session
from ptmd.database import Organism, Chemical, Organisation
from .create_gdrive_file import CreateGDriveFile


def create_gdrive_file() -> tuple[Response, int]:
    """ Function to create a file in the Google Drive using the data provided by the user. Acquire data from a
    JSON request.

    :return: tuple containing a JSON response and a status code
    """
    session: Session = get_session()
    try:
        user_id = get_jwt()['sub']
        payload: CreateGDriveFile = CreateGDriveFile()
        response: dict[str, str] = payload.generate_file(session=session, user=user_id)
        session.close()
        return jsonify({"data": {'file_url': response['alternateLink']}}), 200
    except Exception as e:
        session.close()
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


def get_organisations() -> tuple[Response, int]:
    """ Function to get the organisations from the database.

    :return: tuple containing a JSON response and a status code
    """
    session: Session = get_session()
    response: list[Organisation] = session.query(Organisation).all()
    organisations: dict[str, list[dict[str, int or str]]] = {"data": [dict(organisation) for organisation in response]}
    session.close()
    return jsonify(organisations), 200
