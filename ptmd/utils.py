""" This module contains utility functions for the application. It contains the initialization function that will create
the database and the Google Drive directories.

@author: D. Batista (Terazus)
"""
from os.path import exists

from sqlalchemy.orm import session as sqlsession
from yaml import dump

from ptmd.lib import GoogleDriveConnector, parse_chemicals, parse_organisms
from ptmd.database import boot, User, Organisation, get_session
from ptmd.const import SETTINGS_FILE_PATH, CONFIG
from ptmd.logger import LOGGER


def initialize(users: list[dict], session: sqlsession) -> tuple[dict[str, User], dict[str, Organisation]]:
    """ Initialize the application. This will the directories on Google Drive, get their
    identifiers and create the database with partners and users.

    :param users: A list of users to be created. Organisations can be provided as objects or strings
    :param session: the database SQLAlchemy session
    :return: A tuple containing the organisations and users from the database.
    """
    connector = GoogleDriveConnector()
    users_from_database = session.query(User).all()
    if not users_from_database:
        chemicals_source = parse_chemicals()
        organisms = parse_organisms()
        folders = connector.create_directories()
        organisations, users, chemicals, organisms = boot(organisations=folders['partners'],
                                                          chemicals=chemicals_source,
                                                          users=users,
                                                          organisms=organisms,
                                                          insert=True, session=session)
        return organisations, users

    organisations = session.query(Organisation).all()
    return ({user.username: user.id for user in users_from_database},
            {org.name: org.gdrive_id for org in organisations})


def create_config_file():
    """ A function to create the Google Drive setting file in case it doesn't exist """
    settings_data = {
        'client_config_backend': 'settings',
        'client_config': {
            'client_id': CONFIG['GOOGLE_DRIVE_CLIENT_ID'],
            'client_secret': CONFIG['GOOGLE_DRIVE_CLIENT_SECRET'],
        },
        'save_credentials': True,
        'save_credentials_backend': 'file',
        'save_credentials_file': CONFIG['GOOGLE_DRIVE_CREDENTIALS_FILEPATH'],
        'get_refresh_token': True,
        'oauth_scope': ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.install']
    }
    if not exists(SETTINGS_FILE_PATH):
        LOGGER.info('Creating settings file')
        with open(SETTINGS_FILE_PATH, 'w') as settings_file:
            dump(settings_data, settings_file, default_flow_style=False)
    return settings_data


def init():
    """ Initialize the API """
    LOGGER.info('Initializing the application')
    create_config_file()
    session = get_session()
    initialize(users=[{'username': 'admin', 'password': 'admin', 'organisation': 'UOX'}], session=session)
    session.close()
