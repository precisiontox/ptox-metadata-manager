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

from ptmd.database import Organism, Chemical, Organisation
from .utils import check_role


@check_role(role='enabled')
def get_organisms() -> tuple[Response, int]:
    """ Function to get the organisms from the database.

    :return: tuple containing a JSON response and a status code
    """
    return jsonify({"data": [dict(organism) for organism in Organism.query.all()]}), 200


@check_role(role='enabled')
def get_chemicals() -> tuple[Response, int]:
    """ Function to get the chemicals from the database.

    :return: tuple containing a JSON response and a status code
    """
    return jsonify({"data": [dict(chemical) for chemical in Chemical.query.filter(Chemical.ptx_code < 998).all()]}), 200


@check_role(role='enabled')
def get_organisations() -> tuple[Response, int]:
    """ Function to get the organisations from the database.

    :return: tuple containing a JSON response and a status code
    """
    return jsonify({"data": [dict(organisation) for organisation in Organisation.query.all()]}), 200
