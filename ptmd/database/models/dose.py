""" This module contains the dose table.
"""
from typing import Generator

from ptmd.config import Base, db
from ptmd.database.models.chemical import Chemical
from ptmd.database.models.organism import Organism


class Dose(Base):
    """ The dose table.
    """
    __tablename__: str = 'dose'
    dose_id: int = db.Column(db.Integer, primary_key=True)
    value: float = db.Column(db.Float, nullable=False)
    unit: str = db.Column(db.String(100), nullable=False)
    label: str = db.Column(db.String(10), nullable=False)

    # relationships to organism and chemical
    organism_id: int = db.Column(db.Integer, db.ForeignKey('organism.organism_id'), nullable=False)
    organism = db.relationship(Organism, backref=db.backref('doses'))
    chemical_id: int = db.Column(db.Integer, db.ForeignKey('chemical.chemical_id'), nullable=False)
    chemical = db.relationship(Chemical, backref=db.backref('doses'))

    files = db.relationship('File', secondary='files_doses', back_populates='doses')

    def __iter__(self) -> Generator:
        """ Iterator for the object. Used to serialize the object as a dictionary. """
        output: dict = {
            'value': self.value,
            'unit': self.unit,
            'label': self.label,
            'organism': self.organism.ptox_biosystem_name,
            'chemical': self.chemical.common_name,
            'files': [file.file_id for file in self.files]
        }
        for key, value in output.items():
            yield key, value
