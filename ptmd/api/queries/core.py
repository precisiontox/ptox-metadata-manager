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
from flask import jsonify, Response

from sqlalchemy.orm import Session

from ptmd.utils import get_session
from ptmd.database import Organism, Chemical, Organisation


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
