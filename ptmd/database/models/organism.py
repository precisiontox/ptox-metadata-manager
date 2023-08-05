""" This module contains the organism model. This table represent the species that are used in the project.
"""
from ptmd.config import Base, db


class Organism(Base):
    """ Organism creator.

    :param ptox_biosystem_name: pretox biosystem name
    :param scientific_name: scientific name
    :param ptox_biosystem_code: pretox biosystem code
    """
    __tablename__: str = 'organism'
    organism_id: int = db.Column(db.Integer, primary_key=True)
    ptox_biosystem_name: str = db.Column(db.String(100), nullable=False, unique=True)
    scientific_name: str = db.Column(db.String(100), nullable=False)
    ptox_biosystem_code: str = db.Column(db.String(1), nullable=False, unique=True)

    def __iter__(self):
        """ Iterator for the object. Used to serialize the object as a dictionary. """
        organism: dict = {
            'organism_id': self.organism_id,
            'scientific_name': self.scientific_name,
            'ptox_biosystem_name': self.ptox_biosystem_name,
            'ptox_biosystem_code': self.ptox_biosystem_code
        }
        for key, value in organism.items():
            yield key, value
