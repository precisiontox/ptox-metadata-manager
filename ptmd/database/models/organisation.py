""" This module contains the organisation table. This table represent the consortium partners.
"""
from typing import Any

from flask_jwt_extended import get_current_user

from ptmd.config import Base, db


class Organisation(Base):
    """ Organisation creator.

    :param name: The base class for the creator.
    :param gdrive_id: The Google Drive ID of the corresponding folder.
    """
    __tablename__: str = 'organisation'
    organisation_id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False, unique=True)
    gdrive_id: str = db.Column(db.String(100), nullable=True, unique=True)
    longname: str = db.Column(db.String(100), nullable=True)

    def __iter__(self):
        """ Iterator for the object. Used to serialize the object as a dictionary.  """
        organisation: dict = {
            'name': self.name,
            'longname': self.longname if self.longname else None
        }
        current_user: Any = get_current_user()
        if current_user and current_user.role in ['admin', 'enabled', 'user']:
            organisation['files'] = [file.file_id for file in self.files]
            organisation['gdrive_id'] = self.gdrive_id if self.gdrive_id else None
            organisation['organisation_id'] = self.organisation_id
        for key, value in organisation.items():
            yield key, value
