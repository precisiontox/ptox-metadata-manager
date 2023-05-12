""" This module contains all queries related to organisations.

@author: D. Batista (Terazus)
"""
from ptmd.config import session
from ptmd.logger import LOGGER
from ptmd.database.models import Organisation


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
