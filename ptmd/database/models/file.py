""" This module contains the File database creator.
A file represents an identifier pointing to a specific Google Drive file.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from ptmd.config import Base, db
from ptmd.database.models.organisation import Organisation
from ptmd.database.models.organism import Organism
from ptmd.database.models.chemical import Chemical
from ptmd.database.models.relationship import files_doses, files_chemicals


class File(Base):
    """ File database creator.

    :param gdrive_id: Google Drive file identifier.
    :param name: File name.
    :param batch: Batch name.
    :param replicates: Number of replicates.
    :param controls: Number of controls.
    :param blanks: Number of blanks (empty tubes).
    :param organisation_name: Organisation name.
    :param user_id: User identifier.
    :param organism_name: Organism name.
    :param batch: Batch name.

    :param doses: List of doses.
    :param chemicals: List of chemicals.
    """
    __tablename__: str = 'file'
    file_id: int = db.Column(db.Integer, primary_key=True)
    gdrive_id: str = db.Column(db.String(255), nullable=False)
    name: str = db.Column(db.String(255), nullable=True)
    batch: str = db.Column(db.String(2), nullable=False)
    validated: str = db.Column(db.String(1), nullable=False, default='No')
    replicates: int = db.Column(db.Integer, nullable=False, default=1)
    controls: int = db.Column(db.Integer, nullable=False, default=1)
    blanks: int = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    organisation_id: int = db.Column(db.Integer, db.ForeignKey('organisation.organisation_id'), nullable=False)
    organisation = db.relationship('Organisation', backref=db.backref('files'))
    author_id: int = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('files'))
    organism_id: int = db.Column(db.Integer, db.ForeignKey('organism.organism_id'), nullable=False)
    organism = db.relationship('Organism', backref=db.backref('files'))
    vehicle_id: int = db.Column(db.Integer, db.ForeignKey('chemical.chemical_id'), nullable=False)
    vehicle = db.relationship('Chemical', backref=db.backref('files'))

    # Relationships many-to-many
    chemicals = db.relationship('Chemical', secondary=files_chemicals, back_populates='used_in_files')

    doses = db.relationship('Dose', secondary=files_doses, back_populates='files')

    def __init__(
            self,
            gdrive_id: str,
            name: str,
            batch: str,
            replicates: int,
            controls: int,
            blanks: int,
            organisation_name: str,
            user_id: int,
            organism_name: str,
            vehicle_name: str,
            doses: list | None = None,
            chemicals: list | None = None
    ) -> None:
        """ The File Model constructor """
        self.gdrive_id: str = gdrive_id
        self.name: str = name
        self.batch: str = batch
        self.replicates: int = replicates
        self.controls: int = controls
        self.blanks: int = blanks
        self.author_id: int = user_id

        self.vehicle_id = Chemical.query.filter_by(common_name=vehicle_name).first().chemical_id
        self.organism_id = Organism.query.filter_by(ptox_biosystem_name=organism_name).first().organism_id
        self.organisation_id = Organisation.query.filter_by(name=organisation_name).first().organisation_id

        self.chemicals = chemicals if chemicals else []
        self.doses = doses if doses else []

    def __iter__(self):
        """ Iterator for the object. Used to serialize the object as a dictionary. """
        output: dict = {
            'file_id': self.file_id,
            'gdrive_id': self.gdrive_id,
            'name': self.name,
            'batch': self.batch,
            'replicates': self.replicates,
            'controls': self.controls,
            'blanks': self.blanks,

            'organisation': self.organisation.name if self.organisation else None,
            'author': self.author.username if self.author else None,
            'organism': self.organism.ptox_biosystem_name if self.organism else None,
            'vehicle': self.vehicle.common_name if self.vehicle else None,
            'chemicals': [chemical.common_name for chemical in self.chemicals],

            'doses': [{"value": dose.value, "unit": dose.unit, "label": dose.label} for dose in self.doses]
        }
        for key, value in output.items():
            yield key, value
