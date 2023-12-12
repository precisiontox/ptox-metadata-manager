""" A module to handle the update of file batch. This module contains the BatchUpdater class.
It requires multiple interaction with the database, the local filesystem and the Google Drive API.
"""

from __future__ import annotations

from os import remove

from flask import jsonify, Response
from flask_jwt_extended import get_current_user
from pandas import read_excel, DataFrame, Series, concat as pd_concat

from ptmd.config import session
from ptmd.const import PTX_ID_LABEL
from ptmd.database import File, User, get_shipped_file
from ptmd.lib import save_to_excel, GoogleDriveConnector


class BatchUpdater:
    """ Class to update the batch of a file. Works both with files in the database and local files.

    :param batch: the new batch
    :param file_id: the id of the file to be updated from the database
    :param filepath: the path of the file to be updated from the local filesystem
    """
    old_batch: str
    file_id: int
    filepath: str
    organisation_name: str

    def __init__(self, batch: str, file_id: int | None = None, filepath: str | None = None) -> None:
        """ Constructor method """
        self.new_batch: str = batch
        if file_id and filepath:
            raise ValueError("Provide only one file_id or filepath, not both")
        if not file_id and not filepath:
            raise ValueError("Provide a file_id or filepath")

        if file_id:
            self.file_id = file_id
            self.file: File = self.modify_in_db()
        elif filepath:
            self.filepath = filepath
            self.modify_in_file()

    def modify_in_file(self) -> str:
        """ Method to modify the batch in the file from the local filesystem """
        general_information: DataFrame = read_excel(self.filepath, sheet_name="General Information")
        exposure_information: DataFrame = read_excel(self.filepath, sheet_name="Exposure information")
        samples: list = exposure_information.to_dict(orient='records')
        general_data: dict = general_information.to_dict(orient='records')[0]
        self.old_batch: str = general_data['exposure_batch']
        self.organisation_name = general_data['partner_id']
        general_data['exposure_batch'] = self.new_batch

        new_exposure_information: DataFrame = DataFrame(columns=exposure_information.columns)
        new_general_information: DataFrame = DataFrame(columns=general_information.columns)
        general_info_series: Series = Series([val for key, val in general_data.items()],
                                             index=new_general_information.columns)
        new_general_information = pd_concat([new_general_information, general_info_series.to_frame().T],
                                            ignore_index=True, sort=False)

        for sample in samples:
            identifier_array = list(sample[PTX_ID_LABEL])
            identifier_array[1:3] = self.new_batch
            sample[PTX_ID_LABEL] = ''.join(identifier_array)
            series: Series = Series([val for key, val in sample.items()], index=new_exposure_information.columns)
            new_exposure_information = pd_concat([new_exposure_information, series.to_frame().T],
                                                 ignore_index=True, sort=False)
        save_to_excel((new_exposure_information, new_general_information), self.filepath)
        return self.old_batch

    def modify_in_db(self) -> File:
        """ Method to modify the batch in the file from the database """
        file: File = File.query.filter_by(file_id=self.file_id).first()
        if not file:
            raise BatchError("No file found", 404)
        if file.batch == self.new_batch:
            raise BatchError("Could not update: the new batch and old batch have the same value", 400)
        if file.shipped:
            raise BatchError("File already shipped", 400)

        current_user: User = get_current_user()
        if file.author_id != current_user.id and current_user.role != 'admin':
            raise BatchError("You are authorized to do this", 403)

        if get_shipped_file(file.organism.ptox_biosystem_name, file.batch) and not self.new_batch:
            raise BatchError(f"Batch already used with {file.organism.ptox_biosystem_name}", 412)

        try:
            google_drive: GoogleDriveConnector = GoogleDriveConnector()
            filepath = google_drive.download_file(file.gdrive_id, file.name)
            self.filepath = filepath
            self.old_batch = self.modify_in_file()

            new_filename: str = file.name.replace(self.old_batch, self.new_batch)
            google_drive.update_file(file.gdrive_id, filepath, new_filename)
            remove(filepath)

            file.name = new_filename
            file.batch = self.new_batch
            session.commit()

            return file

        except Exception as e:
            session.rollback()
            raise BatchError(str(e), 500)


class BatchError(Exception):
    """ A custom exception class to handle errors in the BatchUpdater class. This lets us return a response
    with a custom message and status code. We may want to make this a generic class to handle all errors.
    """

    def __init__(self, message: str, code: int) -> None:
        """ Constructor method """
        self.message: str = message
        self.code: int = code
        super().__init__(self.message)

    def serialize(self) -> tuple[Response, int]:
        """ Method to serialize the exception into a tuple containing a JSON response and a status code

        :return: a tuple containing a JSON response and a status code
        """
        return jsonify({"message": self.message}), self.code
