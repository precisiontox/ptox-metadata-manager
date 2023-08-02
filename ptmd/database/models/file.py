""" This module contains the File database creator.
A file represents an identifier pointing to a specific Google Drive file.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from typing import Generator
from datetime import datetime

from flask_jwt_extended import get_current_user

from ptmd.config import Base, db, session
from ptmd.lib.gdrive import GoogleDriveConnector
from ptmd.database.models.organisation import Organisation
from ptmd.database.models.organism import Organism
from ptmd.database.models.chemical import Chemical
from ptmd.database.models.user import User
from ptmd.database.models.relationship import files_doses, files_chemicals, files_timepoints


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
    :param timepoints: List of timepoints.
    :param start_date: Start date of the experiment.
    :param end_date: End date of the experiment.
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

    # Shipping status
    shipped: bool = db.Column(db.Boolean, nullable=False, default=False)
    received: bool = db.Column(db.Boolean, nullable=False, default=False)

    # Dates
    start_date: datetime = db.Column(db.DateTime, nullable=False)
    end_date: datetime = db.Column(db.DateTime, nullable=False)
    # send_date: datetime = db.Column(db.DateTime, nullable=True)
    # receive_date: datetime = db.Column(db.DateTime, nullable=True)

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
    timepoints = db.relationship('Timepoint', secondary=files_timepoints, back_populates='files', cascade='all, delete')

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
            start_date: str,
            end_date: str,
            doses: list | None = None,
            chemicals: list | None = None,
            timepoints: list | None = None
    ) -> None:
        """ The File Model constructor """
        self.gdrive_id = gdrive_id
        self.name = name
        self.batch = batch
        self.replicates = replicates
        self.controls = controls
        self.blanks = blanks
        self.author_id = user_id

        self.vehicle_id = Chemical.query.filter_by(common_name=vehicle_name).first().chemical_id
        self.organism_id = Organism.query.filter_by(ptox_biosystem_name=organism_name).first().organism_id
        self.organisation_id = Organisation.query.filter_by(name=organisation_name).first().organisation_id

        self.chemicals = chemicals if chemicals else []
        self.doses = doses if doses else []
        self.timepoints = timepoints if timepoints else []

        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')

    def __iter__(self) -> Generator:
        """ Iterator for the object. Used to serialize the object as a dictionary. """
        output: dict = {
            'file_id': self.file_id,
            'gdrive_id': self.gdrive_id,
            'name': self.name,
            'batch': self.batch,
            'replicates': self.replicates,
            'controls': self.controls,
            'blanks': self.blanks,

            'shipped': self.shipped,
            'received': self.received,

            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),

            'organisation': self.organisation.name if self.organisation else None,
            'author': self.author.username if self.author else None,
            'organism': self.organism.ptox_biosystem_name if self.organism else None,
            'vehicle': self.vehicle.common_name if self.vehicle else None,
            'chemicals': [chemical.common_name for chemical in self.chemicals],
            'timepoints': [dict(timepoint) for timepoint in self.timepoints],
            'validated': self.validated,

            'doses': [{"value": dose.value, "unit": dose.unit, "label": dose.label} for dose in self.doses]
        }

        for key, value in output.items():
            yield key, value

    def remove(self) -> None:
        """ Remove the file from the database. """
        current_user: User = get_current_user()
        if current_user != self.author and current_user.role != 'admin':
            raise PermissionError(f"You don't have permission to delete file {self.file_id}.")

        try:
            connector: GoogleDriveConnector = GoogleDriveConnector()
            connector.delete_file(self.gdrive_id)
        except PermissionError:
            # we can just pass here and delete the file from the database without deleting the file from the drive
            pass
        finally:
            session.delete(self)  # type: ignore
            session.commit()

    def shipment_was_received(self) -> None:
        """ Update the shipment status of the file. This method is called when the shipment is received.
        """
        user: User = get_current_user()
        if user.role != 'admin':
            raise PermissionError(f"You don't have permission to update to receive shipment for file {self.file_id}.")
        if not self.shipped:
            raise ValueError(f"File {self.file_id} has not been shipped yet.")
        self.received = True
        session.commit()

    def ship_samples(self) -> None:
        """ Ship the samples to the user. """
        user: User = get_current_user()
        if user != self.author and user.role != 'admin':
            raise PermissionError(f"You don't have permission to ship file {self.file_id}.")
        if self.validated != 'success':
            raise ValueError(f"File {self.file_id} has not been validated yet or has failed validation.")
        if self.shipped:
            raise ValueError(f"File {self.file_id} has already been shipped.")
        self.shipped = True
        session.commit()
