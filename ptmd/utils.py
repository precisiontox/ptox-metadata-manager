""" This module contains utility functions for the application. It contains the initialization function that will create
the database and the Google Drive directories.

@author: D. Batista (Terazus)
"""
from os.path import exists
from yaml import dump

from ptmd.lib import GoogleDriveConnector, parse_chemicals, parse_organisms
from ptmd.config import app, engine
from ptmd.database import boot, User, Organisation
from ptmd.const import SETTINGS_FILE_PATH, CONFIG
from ptmd.logger import LOGGER
from ptmd.database import Base


def initialize(users: list[dict]) -> tuple:
    """ Initialize the application. This will the directories on Google Drive, get their
    identifiers and create the database with partners and users.

    :param users: A list of users to be created. Organisations can be provided as objects or strings
    :return: A tuple containing the organisations and users from the database.
    """
    Base.metadata.create_all(engine)
    with app.app_context():
        connector = GoogleDriveConnector()
        users_from_database = User.query.all()
        if not users_from_database:
            chemicals_source = parse_chemicals()
            organisms = parse_organisms()
            folders: dict = connector.create_directories()
            [organisations, users, _, __] = boot(organisations=folders['partners'],
                                                 chemicals=chemicals_source,
                                                 users=users,
                                                 organisms=organisms,
                                                 insert=True)
            return organisations, users
        organisations = Organisation.query.all()
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
        'oauth_scope': [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/drive.install',
            'https://www.googleapis.com/auth/gmail.send',
        ]
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
    initialize(users=[{'username': 'admin', 'password': 'admin', 'organisation': 'UOX'}])
