""" This module contains all queries related to chemicals.

@author: D. Batista (Terazus)
"""
from ptmd.config import session
from ptmd.logger import LOGGER
from ptmd.database.models import Chemical


def get_allowed_chemicals() -> list[str]:
    """ Get the list of allowed chemicals names.

    :return: a list of chemicals names
    """
    return [chemical.common_name for chemical in Chemical.query.all()]


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


def get_chemicals_from_name(chemicals: list[str]) -> list[Chemical]:
    """ Get the chemicals from the database.

    :return: a list of chemicals from the database
    """
    LOGGER.info('Getting Chemicals')
    return Chemical.query.filter(Chemical.common_name.in_(chemicals)).all()
