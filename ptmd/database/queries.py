""" This module contains functions to interact with the database such as boot(), create_organisations(),
create_users(). login_user() and get_allowed_chemicals().

:author: D. Batista (Terazus)
"""

from datetime import timedelta
from ptmd.logger import LOGGER

from flask_jwt_extended import create_access_token
from flask import jsonify, Response
from sqlalchemy.orm import session as sqlsession

from ptmd.database.utils import get_session
from .models import User, Organisation, Chemical, Organism


def boot(
        session: sqlsession,
        organisations: dict = (),
        users: list[dict] = (),
        chemicals: list[dict] = (),
        organisms: list[dict] = (),
        insert: bool = False
) -> list[dict[str, Organisation], dict[str, User], dict[str, Chemical], dict[str, Organism]]:
    """ Boot the database. This will create all tables and insert the default users.

    :param session: the database SQLAlchemy session
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
        created_organisations = create_organisations(organisations=organisations, session=session)
        created_users = create_users(users=users, session=session)
        created_chemicals = create_chemicals(chemicals=chemicals, session=session)
        created_organisms = create_organisms(organisms=organisms, session=session)
    LOGGER.info('Database boot completed')
    return [created_organisations, created_users, created_chemicals, created_organisms]


def login_user(username: str, password: str, session: sqlsession) -> tuple[Response, int]:
    """ Login a user and return a JWT token. The username and password are retrieved from the request body.

    @param username
    @param password
    @param session: the database session
    @return: Response, int: the response message and the response code
    """
    user = session.query(User).filter_by(username=username).first()
    t = session.query(User).first()
    user = dict(user) if user and user.validate_password(password) else None
    if not user:
        return jsonify({"msg": "Bad username or password"}), 401
    access_token = create_access_token(identity=user['id'], expires_delta=timedelta(days=1000000))
    return jsonify(access_token=access_token), 200


def get_allowed_chemicals() -> list[str]:
    """ Get the list of allowed chemicals names.

    :return: a list of chemicals names
    """
    session: sqlsession = get_session()
    allowed_chemicals = [chemical.common_name for chemical in session.query(Chemical).all()]
    session.close()
    return allowed_chemicals


def get_allowed_organisms() -> list[str]:
    """ Get the list of allowed organisms names.

    :return: a list of organisms names
    """
    session: sqlsession = get_session()
    allowed_organism = [organism.ptox_biosystem_name for organism in session.query(Organism).all()]
    session.close()
    return allowed_organism


def get_organism_code(organism_name: str) -> str | None:
    """ Get the organism code from the organism name."""
    session: sqlsession = get_session()
    organism = session.query(Organism).filter_by(ptox_biosystem_name=organism_name).first()
    session.close()
    return organism.ptox_biosystem_code if organism else None


def get_chemical_code_mapping(chemicals: list[str]) -> dict[str, str]:
    """ Get the chemical code from the chemical name.

    :param chemicals: list[str]: list of chemicals names
    :return: list of chemicals codes
    """
    session: sqlsession = get_session()
    chemicals_mapping = {}
    for chemical in chemicals:
        chemical = session.query(Chemical).filter_by(common_name=chemical).first()
        chemicals_mapping[chemical.common_name] = str(chemical.ptx_code).rjust(3, '0')
    session.close()
    return chemicals_mapping


def create_organisations(organisations: dict, session: sqlsession) -> dict[str, Organisation]:
    """ Create organisations in the database.

    :param organisations: list[str]: list of organisations names
    :param session: the database SQLAlchemy session
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
        organisation[org] = session.query(Organisation).filter_by(name=org).first()
    return organisation


def create_users(users: list[dict], session: sqlsession) -> dict[int, User]:
    """ Create users in the database.

    :param users: list[dict]: list of users
    :param session: the database SQLAlchemy session
    :return: bool: True if the users were created, False otherwise
    """
    LOGGER.info('Creating users')
    created_users = {}
    for user_index, user in enumerate(users):
        session.add(User(**user, session=session))
        user_from_db = session.query(User).filter_by(username=user['username']).first()
        created_users[user_index] = user_from_db
    session.commit()
    return created_users


def create_chemicals(chemicals: list[dict], session: sqlsession) -> dict[str, Chemical]:
    """ Creates the chemicals in the database.

    :param chemicals: list of chemicals coming from the precision toxicology API
    :param session: the database SQLAlchemy session
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


def create_organisms(organisms: list[dict], session: sqlsession) -> dict[str, Organism]:
    """ Creates the organisms in the database.

    :param organisms: list of organisms coming from the precision toxicology API
    :param session: the database SQLAlchemy session
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
