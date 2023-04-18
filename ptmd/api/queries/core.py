""" This module contains the functions triggered by the API endpoints.
It includes:
    - login_user to log in a user
    - register_gdrive_file to register an existing file from an external Google Drive in the database
    - create_gdrive_file to create a file in the Google Drive using the data provided by the user
    - get_organisms to get the organisms from the database
    - get_chemicals to get the chemicals from the database
    - change_password to change the password of the current user

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from re import match

from flask import jsonify, Response, request
from flask_jwt_extended import get_jwt
from sqlalchemy.orm import Session

from ptmd.utils import get_session
from ptmd.const import ALLOWED_EXPOSURE_BATCH
from ptmd.database import Organism, Chemical, Organisation, File, User
from ptmd.clients.gdrive import GoogleDriveConnector
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


def register_gdrive_file() -> tuple[Response, int]:
    """ Function to register an already existing file from an external Google Drive. Requires the file to
    be 'readable by everyone with the link'.

    :return: tuple containing a JSON response and a status code
    """
    required_fields: list[str] = ['file_id', 'batch', 'organism']
    session = get_session()
    try:
        for field in required_fields:
            if field not in request.json or request.json[field] == "":
                raise ValueError(f'Field {field} is required.')

        file_id: str = request.json['file_id']
        user_id: int = get_jwt()['sub']
        batch: str = request.json['batch']
        organisation: Organisation = session.query(User).filter(User.id == user_id).first().organisation
        connector: GoogleDriveConnector = GoogleDriveConnector()
        if not match(ALLOWED_EXPOSURE_BATCH, batch):
            raise ValueError(f"Batch '{batch}' has an incorrect format.")

        file: File = File(gdrive_id=file_id,
                          batch=batch,
                          organism_name=request.json['organism'],
                          name=connector.get_filename(file_id),
                          organisation_name=organisation.name,
                          user_id=user_id,
                          session=session)
        session.add(file)
        session.commit()
        msg: str = f'file {file_id} was successfully created with internal id {file.file_id}'
        return jsonify({"data": {"message": msg, "file": file.file_id}}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
    finally:
        session.close()


def get_organisms() -> tuple[Response, int]:
    """ Function to get the organisms from the database.

    :return: tuple containing a JSON response and a status code
    """
    session: Session = get_session()
    organisms: dict[str, list[dict[str, int | str]]] = {
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
    chemicals: dict = {"data": [dict(chemical) for chemical in response]}
    session.close()
    return jsonify(chemicals), 200


def get_organisations() -> tuple[Response, int]:
    """ Function to get the organisations from the database.

    :return: tuple containing a JSON response and a status code
    """
    session: Session = get_session()
    response: list[Organisation] = session.query(Organisation).all()
    organisations: dict[str, list] = {"data": [dict(organisation) for organisation in response]}
    session.close()
    return jsonify(organisations), 200
