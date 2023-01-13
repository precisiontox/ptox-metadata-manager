""" This module contains the organisation model.

@author: D. Batista (Terazus)
"""
from ptmd.config import Base, db


class Organisation(Base):
    """ Organisation model.

    :param name: The base class for the model.
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
            'organisation_id': self.organisation_id,
            'name': self.name,
            'gdrive_id': self.gdrive_id if self.gdrive_id else None,
            'longname': self.longname if self.longname else None,
            'files': [dict(file) for file in self.files]
        }
        for key, value in organisation.items():
            yield key, value
