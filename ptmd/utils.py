""" This module contains utility functions for the application. It contains the initialization function that will create
the database and the Google Drive directories.

@author: D. Batista (Terazus)
"""

from sqlalchemy.orm import session as sqlsession

from ptmd.clients import GoogleDriveConnector, pull_chemicals_from_ptox_db, pull_organisms_from_ptox_db
from ptmd.database import boot, User, Organisation


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
        chemicals_source = pull_chemicals_from_ptox_db()
        organisms = pull_organisms_from_ptox_db()
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
