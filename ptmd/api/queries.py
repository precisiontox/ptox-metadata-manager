""" All queries related to the dataabase and the Google Drive integration are defined here.
It contains:
    - login_user to log in a user
    - get_me to get the current user
    - create_gdrive_file to create a file in the Google Drive using the data provided by the user

:author: D. Batista (Terazus)
"""
from os import path

from flask import jsonify, request, Response
from flask_jwt_extended import get_jwt
from sqlalchemy.orm import Session

from ptmd import HarvesterInput, GoogleDriveConnector
from ptmd.const import ROOT_PATH
from ptmd.database import login_user, User, Organisation, Organism, Chemical
from .utils import get_session


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
    session.close()
    return login_user(username=username, password=password, session=session)


def get_me() -> tuple[Response, int]:
    """ Function to get the current user. Acquire data from the JWT

    :return: tuple containing a JSON response and a status code
    """
    try:
        session: Session = get_session()
        user_id: int = get_jwt()['sub']
        user: User = session.query(User).filter_by(id=user_id).first()
        session.close()
        return jsonify(dict(user)), 200
    except Exception:
        return jsonify({"msg": "Invalid token"}), 401


def create_gdrive_file() -> tuple[Response, int]:
    """ Function to create a file in the Google Drive using the data provided by the user. Acquire data from a
    JSON request.

    :return: tuple containing a JSON response and a status code
    """
    directory_path: str = path.join(ROOT_PATH, 'resources')
    data: dict = {
        'partner': request.json.get('partner', None),
        'organism': request.json.get('organism', None),
        'exposure_batch': request.json.get('exposure_batch', None),
        'replicate_blank': request.json.get('replicate_blank', None),
        'start_date': request.json.get('start_date', None),
        'end_date': request.json.get('end_date', None),
        'exposure_conditions': request.json.get('exposure_conditions', None),
        'replicate4control': request.json.get('replicate4control', None),
        'replicate4exposure': request.json.get('replicate4exposure', None),
    }
    try:
        filename: str = f"{data['partner']}_{data['organism']}_{data['exposure_batch']}.xlsx"
        filepath: str = path.join(directory_path, filename)
        inputs: HarvesterInput = HarvesterInput(**data)
        inputs.save_file(filepath)
        session: Session = get_session()
        folder_id: str = session.query(Organisation).filter_by(name=data['partner']).first().gdrive_id
        session.close()
        gdrive: GoogleDriveConnector = GoogleDriveConnector()
        response: dict = gdrive.upload_file(directory_id=folder_id, file_path=filepath)
        inputs.delete_file()
        return jsonify({"data": {'file_url': response['alternateLink']}}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400


def get_organisms() -> tuple[Response, int]:
    """ Function to get the organisms from the database.

    :return: tuple containing a JSON response and a status code
    """
    session: Session = get_session()
    organisms: dict[str, list] = {"data": [dict(organism) for organism in session.query(Organism).all()]}
    session.close()
    return jsonify(organisms), 200


def get_chemicals() -> tuple[Response, int]:
    """ Function to get the chemicals from the database.

    :return: tuple containing a JSON response and a status code
    """
    session: Session = get_session()
    chemicals: dict[str, list] = {"data": [dict(chemical) for chemical in session.query(Chemical).all()]}
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
