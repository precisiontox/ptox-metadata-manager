""" This module contains the Chemical database creator.

@author: D. Batista (Terazus)
"""
from typing import Generator

from ptmd.config import Base, db


class Chemical(Base):
    """ The chemical creator.

    :param common_name: The base class for the creator.
    :param cas: The name hash id.
    :param formula: The chemical formula.
    :param ptx_code: The PTX code.
    """
    __tablename__: str = 'chemical'
    chemical_id: int = db.Column(db.Integer, primary_key=True)
    common_name: str = db.Column(db.String(100), nullable=False, unique=True)
    cas: str = db.Column(db.String(100), nullable=True)
    formula: str = db.Column(db.String(100), nullable=False)
    ptx_code: int = db.Column(db.Integer, nullable=False, unique=True)

    def __iter__(self) -> Generator:
        """ Iterator for the object. Used to serialize the object as a dictionary. """
        chemical: dict = {
            'chemical_id': self.chemical_id,
            'common_name': self.common_name,
            'cas': self.cas,
            'formula': self.formula,
            'ptx_code': self.ptx_code if self.ptx_code else None
        }
        for key, value in chemical.items():
            yield key, value
