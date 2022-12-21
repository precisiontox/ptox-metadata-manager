""" This module contains the Chemical database model.

@author: D. Batista (Terazus)
"""
from ptmd.config import Base, db


class Chemical(Base):
    """ The chemical model.

    :param common_name: The base class for the model.
    :param name_hash_id: The name hash id.
    :param formula: The chemical formula.
    :param ptx_code: The PTX code.
    """
    __tablename__: str = 'chemical'
    chemical_id: int = db.Column(db.Integer, primary_key=True)
    common_name: str = db.Column(db.String(100), nullable=False, unique=True)
    name_hash_id: str = db.Column(db.String(100), nullable=True)
    formula: str = db.Column(db.String(100), nullable=False)
    ptx_code: int = db.Column(db.Integer, nullable=False, unique=True)

    def __iter__(self) -> None:
        """ Iterator for the object. Used to serialize the object as a dictionary. """
        chemical: dict = {
            'chemical_id': self.chemical_id,
            'common_name': self.common_name,
            'name_hash_id': self.name_hash_id,
            'formula': self.formula,
            'ptx_code': self.ptx_code if self.ptx_code else None
        }
        for key, value in chemical.items():
            yield key, value
