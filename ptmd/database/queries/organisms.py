""" This module contains all queries related to organisms.

@author: D. Batista (Terazus)
"""
from ptmd.config import session
from ptmd.logger import LOGGER
from ptmd.database.models import Organism


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
