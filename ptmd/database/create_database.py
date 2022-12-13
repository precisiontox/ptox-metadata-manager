from sqlalchemy import engine as sql_engine
from sqlalchemy.orm import sessionmaker, session as sqlsession

from ptmd.logger import LOGGER
from .config import db, Base
from .models import User, Organisation


def boot(engine: sql_engine,
         organisations: dict = (),
         users: list[dict] = (),
         drop_all: bool = False,
         insert: bool = False) -> list[dict[str: Organisation], dict[str: User]]:
    """ Boot the database. This will create all tables and insert the default users.

    :param engine: the database SQLAlchemy engine
    :param organisations: list of organisations
    :param users: list of users
    :param drop_all: bool: drop all tables before creating them
    :param insert: bool: insert the default users
    :return: a list containing users and organisations
    """
    if drop_all:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session: sqlsession = sessionmaker(bind=engine)
    session = session()
    created_organisations: dict[str: Organisation] = {}
    created_users: dict[str: User] = {}
    if insert:
        created_organisations = create_organisations(organisations=organisations, session=session)
        created_users = create_users(users=users)
    LOGGER.info('Database boot completed')
    return [created_organisations, created_users]


def create_organisations(organisations: dict, session: sqlsession) -> dict[str: Organisation]:
    """ Create organisations in the database.

    :param organisations: list[str]: list of organisations names
    :param session: the database SQLAlchemy session
    :return: a dictionary with the organisation name as key and the organisation object as value
    """
    for org in organisations:
        session.add(Organisation(name=org, gdrive_id=organisations[org]))
    session.add(Organisation(name='UOX'))
    session.commit()
    organisation = {'UOX': session.query(Organisation).filter_by(name='UOX').first()}
    for org in organisations:
        organisation[org] = session.query(Organisation).filter_by(name=org).first()
    return organisation


def create_users(users: list[dict], session: sqlsession) -> dict[str: User]:
    """ Create users in the database.

    :param users: list[dict]: list of users
    :param session: the database SQLAlchemy session
    :return: bool: True if the users were created, False otherwise
    """
    created_users = {}
    for user_index, user in enumerate(users):
        session.add(User(**user))
        user_from_db = session.query(User).filter_by(username=user['username']).first()
        created_users[user_index] = user_from_db
    session.commit()
    return created_users
