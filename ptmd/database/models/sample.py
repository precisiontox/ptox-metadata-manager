""" This module contains the Sample database schema.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from typing import Generator
from json import dumps as json_dumps, loads as json_loads

from ptmd.config import Base, db


class Sample(Base):
    """ The sample creator.

    """
    __tablename__: str = 'sample'
    sample_id: str = db.Column(db.String(9), primary_key=True)
    data: str = db.Column(db.String(100000), nullable=False)

    file_id: int = db.Column(db.Integer, db.ForeignKey('file.file_id'), nullable=False)
    file = db.relationship('File', backref=db.backref('samples'))

    def __init__(self, sample_id: str, data: dict, file_id: int) -> None:
        """ Constructor for the Sample class.

        :param sample_id: The sample id.
        :param data: The sample data.
        :param file_id: The file id.
        """
        self.sample_id = sample_id
        self.data = json_dumps(data)
        self.file_id = file_id

    def __iter__(self) -> Generator:
        """ Iterator for the object. Used to serialize the object as a dictionary.

        :return: The iterator.
        """
        sample: dict = {
            **json_loads(self.data),
            'organism': self.file.organism.ptox_biosystem_name,
            'organisation': self.file.organisation.longname,
            'batch': self.file.batch,
            'vehicle': dict(self.file.vehicle),
            'google_file': self.file.gdrive_id
        }
        for key, value in sample.items():
            yield key, value
