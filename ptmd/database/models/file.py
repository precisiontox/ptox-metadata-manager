""" This module contains the File database creator.
A file represents an identifier pointing to a specific Google Drive file.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from ptmd.config import Base, db
from ptmd.database.models.organisation import Organisation
from ptmd.database.models.user import User
from ptmd.database.models.organism import Organism


class File(Base):
    """ File database creator.

    :param gdrive_id: Google Drive file identifier.
    :param name: File name.
    :param organisation_name: Organisation name.
    :param user_id: User identifier.
    :param organism_name: Organism name.
    :param batch: Batch name.
    """
    __tablename__: str = 'file'
    file_id: int = db.Column(db.Integer, primary_key=True)
    gdrive_id: str = db.Column(db.String(255), nullable=False)
    name: str = db.Column(db.String(255), nullable=True)
    batch: str = db.Column(db.String(2), nullable=False)
    validated: str = db.Column(db.String(1), nullable=False, default='No')

    # Relationships
    organisation_id: int = db.Column(db.Integer, db.ForeignKey('organisation.organisation_id'), nullable=False)
    organisation = db.relationship(Organisation, backref=db.backref('files'), lazy='subquery')
    author_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship(User, backref=db.backref('files'), lazy='subquery')
    organism_id: int = db.Column(db.Integer, db.ForeignKey('organism.organism_id'), nullable=False)
    organism = db.relationship(Organism, backref=db.backref('files'), lazy='subquery')

    def __init__(
            self,
            gdrive_id: str,
            name: str,
            organisation_name: str,
            user_id: int,
            organism_name: str,
            batch: str
    ) -> None:
        """ The File Model constructor """
        self.gdrive_id: str = gdrive_id
        self.name: str = name
        self.author_id: int = user_id
        self.batch: str = batch
        self.organism_id: int = Organism.query.filter_by(ptox_biosystem_name=organism_name).first().organism_id
        self.organisation_id: int = Organisation.query.filter_by(name=organisation_name).first().organisation_id

    def __iter__(self):
        """ Iterator for the object. Used to serialize the object as a dictionary. """
        output = {
            'file_id': self.file_id,
            'gdrive_id': self.gdrive_id,
            'name': self.name,
            'batch': self.batch,
            'organisation': self.organisation.name if self.organisation else None,
            'author': self.author.username if self.author else None,
            'organism': self.organism.ptox_biosystem_name if self.organism else None
        }
        for key, value in output.items():
            yield key, value
