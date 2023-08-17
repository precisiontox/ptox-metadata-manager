""" This module contains the Chemical database model. Chemicals represent the stimuli that the collected samples are
exposed to.
"""
from __future__ import annotations

from typing import Generator

from sqlalchemy import Column

from ptmd.const import BASE_IDENTIFIER
from ptmd.config import Base, db
from ptmd.database.utils import get_current_user
from ptmd.database.models.user import User
from ptmd.database.models.relationship import files_chemicals


class Chemical(Base):
    """ The chemical creator.

    :param common_name: The base class for the creator.
    :param cas: The name hash id.
    :param formula: The chemical formula.
    :param ptx_code: The PTX code.
    """
    __tablename__: str = 'chemical'
    chemical_id: int = db.Column(db.Integer, primary_key=True)
    common_name: Column = db.Column(db.String(100), nullable=False)
    cas: str = db.Column(db.String(100), nullable=True)
    formula: str = db.Column(db.String(100), nullable=False)
    ptx_code: int = db.Column(db.Integer, nullable=False, unique=True)

    used_in_files = db.relationship('File', secondary=files_chemicals, back_populates='chemicals')

    def __iter__(self) -> Generator:
        """ Iterator for the object. Used to serialize the object as a dictionary. """
        chemical: dict = {
            'common_name': self.common_name,
            'cas': self.cas,
            'formula': self.formula,
            'ptx_code': BASE_IDENTIFIER + str(self.ptx_code).rjust(3, '0')
        }
        current_user: User | None = get_current_user()
        if current_user and current_user.role != 'banned':
            chemical['chemical_id'] = self.chemical_id
        for key, value in chemical.items():
            yield key, value
