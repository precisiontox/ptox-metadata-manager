""" This module contains functions to interact with the database such as boot(), create_organisations(),
create_users(). login_user() and get_allowed_chemicals().

:author: D. Batista (Terazus)
"""
from __future__ import annotations

from datetime import timedelta
from flask_jwt_extended import create_access_token
from flask import jsonify, Response

from ptmd.config import session
from ptmd.logger import LOGGER
from ptmd.database.models import User, Organisation, Chemical, Organism


def boot(
        organisations: dict, users: list[dict], chemicals: list[dict], organisms: list[dict], insert: bool = False
) -> list:
    """ Boot the database. This will create all tables and insert the default users.

    :param organisations: list of organisations
    :param chemicals: list of chemicals coming from the precision toxicology API
    :param users: list of users
    :param organisms: list of organisms coming from the precision toxicology API
    :param insert: bool: insert the default users
    :return: a list containing users and organisations
    """
    created_organisations: dict[str, Organisation] = {}
    created_users: dict[int, User] = {}
    created_chemicals: dict[str, Chemical] = {}
    created_organisms: dict[str, Organism] = {}
    if insert:
        created_organisations = create_organisations(organisations=organisations)
        created_users = create_users(users=users)
        created_chemicals = create_chemicals(chemicals=chemicals)
        created_organisms = create_organisms(organisms=organisms)
    LOGGER.info('Database boot completed')
    return [created_organisations, created_users, created_chemicals, created_organisms]


def login_user(username: str, password: str) -> tuple[Response, int]:
    """ Login a user and return a JWT token. The username and password are retrieved from the request body.

    @param username
    @param password
    @return: Response, int: the response message and the response code
    """
    raw_user = User.query.filter(User.username == username ).first()
    user = dict(raw_user) if raw_user and raw_user.validate_password(password) else None
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=user['id'], expires_delta=timedelta(days=1000000))
    return jsonify(access_token=access_token), 200


def get_allowed_chemicals() -> list[str]:
    """ Get the list of allowed chemicals names.

    :return: a list of chemicals names
    """
    return [chemical.common_name for chemical in Chemical.query.all()]


def get_allowed_organisms() -> list[str]:
    """ Get the list of allowed organisms names.

    :return: a list of organisms names
    """
    return [organism.ptox_biosystem_name for organism in Organism.query.all()]


def get_organism_code(organism_name: str) -> str:
    """ Get the organism code from the organism name.

    :param organism_name: str: the organism name
    :return: str: the organism code
    """
    organism = Organism.query.filter(Organism.ptox_biosystem_name == organism_name).first()
    if not organism:
        raise ValueError(f'Organism {organism_name} not found in the database.')
    return organism.ptox_biosystem_code


def get_chemical_code_mapping(chemicals: list[str]) -> dict[str, str]:
    """ Get the chemical code from the chemical name.

    :param chemicals: list[str]: list of chemicals names
    :return: list of chemicals codes
    """
    chemicals_mapping = {}
    for chemical_name in chemicals:
        chemical: Chemical = Chemical.query.filter(Chemical.common_name == chemical_name).first()
        if not chemical:
            raise ValueError(f'Chemical {chemical_name} not found in the database.')
        chemicals_mapping[chemical.common_name] = str(chemical.ptx_code).rjust(3, '0')
    return chemicals_mapping


def create_organisations(organisations: dict) -> dict:
    """ Create organisations in the database.

    :param organisations: list[str]: list of organisations names
    :return: a dictionary with the organisation name as key and the organisation object as value
    """
    LOGGER.info('Creating organisations')
    for org in organisations:
        session.add(Organisation(name=org,
                                 gdrive_id=organisations[org]['g_drive'],
                                 longname=organisations[org]['long_name']))
    session.commit()
    organisation = {}
    for org in organisations:
        organisation[org] = Organisation.query.filter(Organisation.name == org).first()
    return organisation


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


def create_chemicals(chemicals: list[dict]) -> dict[str, Chemical]:
    """ Creates the chemicals in the database.

    :param chemicals: list of chemicals coming from the precision toxicology API
    :return: a list of chemicals from the database
    """
    LOGGER.info('Creating Chemicals')
    chemicals_in_database = {}
    for chemical in chemicals:
        try:
            chemical_in_database = Chemical(**chemical)
            session.add(chemical_in_database)
            session.commit()
            chemicals_in_database[chemical['common_name']] = chemical_in_database
        except Exception as e:
            LOGGER.error(f'Could not create chemical {chemical} with error {str(e)}')
            session.rollback()
    return chemicals_in_database


def create_organisms(organisms: list[dict]) -> dict[str, Organism]:
    """ Creates the organisms in the database.

    :param organisms: list of organisms coming from the precision toxicology API
    :return: a list of organisms from the database
    """
    LOGGER.info('Creating Organisms')
    organisms_in_database = {}
    for organism in organisms:
        try:
            organism_in_database = Organism(**organism)
            session.add(organism_in_database)
            session.commit()
            organisms_in_database[organism['ptox_biosystem_name']] = organism_in_database
        except Exception as e:
            LOGGER.error(f'Could not create organism {organism} with error {str(e)}')
            session.rollback()
    return organisms_in_database
