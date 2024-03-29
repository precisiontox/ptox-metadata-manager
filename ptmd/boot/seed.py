""" This module contains the database seeder.
"""

from ptmd.logger import LOGGER
from ptmd.database.models import User, Organisation, Chemical, Organism, File
from ptmd.database.queries import create_organisations, create_users, create_chemicals, create_organisms, create_files


def seed_db(
        organisations: dict, users: list[dict], chemicals: list[dict], organisms: list[dict], files: dict
) -> list:
    """ Boot the database. This will create all tables and insert the users, organisations, chemicals and organisms.

    :param organisations: list of organisations to create
    :param chemicals: list of chemicals to create
    :param users: list of users to create
    :param organisms: list of organisms to create
    :param files: list of files to create
    :return: a list containing created objects organised by type
    """
    LOGGER.info('Starting initial seeding of the database')
    created_organisations: dict[str, Organisation] = create_organisations(organisations=organisations)
    created_users: dict[int, User] = create_users(users=users)
    created_chemicals: dict[str, Chemical] = create_chemicals(chemicals=chemicals)
    created_organisms: dict[str, Organism] = create_organisms(organisms=organisms)
    created_files: list[File] = create_files(files_data=files)
    LOGGER.info('Seed completed')
    return [created_organisations, created_users, created_chemicals, created_organisms, created_files]
