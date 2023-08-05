""" This module implements the Timepoint database model. Each timepoint contains a label, a value and a unit.
"""
from typing import Generator

from ptmd.config import Base, db
from ptmd.database.models.relationship import files_timepoints


class Timepoint(Base):
    """ This class implements the Timepoint model. """
    __tablename__: str = 'timepoint'
    timepoint_id: int = db.Column(db.Integer, primary_key=True)
    value: int = db.Column(db.Integer, nullable=False)
    unit: str = db.Column(db.String(255), nullable=False)
    label: str = db.Column(db.String(255), nullable=True)

    files = db.relationship('File', secondary=files_timepoints, back_populates='timepoints')

    def __iter__(self) -> Generator:
        """ This method implements the iterator protocol. """
        yield from {
            'value': self.value,
            'unit': self.unit,
            'label': self.label,
            'files': [file.gdrive_id for file in self.files]
        }.items()
