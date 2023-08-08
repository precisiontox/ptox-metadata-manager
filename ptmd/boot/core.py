""" This module contains the main initializer of the application.
"""
from ptmd.config import app, engine
from ptmd.const import ADMIN_EMAIL, ADMIN_USERNAME, ADMIN_PASSWORD
from ptmd.database import User, Base
from ptmd.lib import GoogleDriveConnector
from ptmd.logger import LOGGER
from .config import create_config_file
from .file_parsers import parse_chemicals, parse_organisms
from .seed import seed_db


DEFAULT_USER: dict = {
    'username': ADMIN_USERNAME,
    'email': ADMIN_EMAIL,
    'password': ADMIN_PASSWORD,
    'role': 'admin'
}


def initialize() -> None:
    """ Initialize the application. This will create the directories on Google Drive and the database
    with seeding for partners, chemicals, organisms, organisations, files and the default admin user.
    """
    LOGGER.info('Initializing the application')
    create_config_file()
    connector: GoogleDriveConnector = GoogleDriveConnector()
    Base.metadata.create_all(engine)

    try:
        with app.app_context():
            if not User.query.first():
                directories, files = connector.create_directories()
                seed_db(organisations=directories['partners'],
                        chemicals=parse_chemicals(),
                        users=[DEFAULT_USER],
                        organisms=parse_organisms(),
                        files=files)
    except Exception as e:
        Base.metadata.drop_all(engine)
        LOGGER.error('Error initializing the application: %s', e)
        raise e
    LOGGER.info('Application initialized')
