""" Module to register an already existing file from an external Google Drive. Requires the file to
be 'readable by everyone with the link'. Will create an entry in the database.
"""
from __future__ import annotations

from os import remove

from flask import jsonify, Response, request
from flask_jwt_extended import get_current_user

from ptmd.logger import LOGGER
from ptmd.config import session
from ptmd.database import Organisation, File, get_shipped_file
from ptmd.lib import BatchUpdater, GoogleDriveConnector
from ptmd.lib.data_extractor import extract_data_from_spreadsheet
from ptmd.api.queries.utils import check_role


@check_role(role='enabled')
def register_gdrive_file() -> tuple[Response, int]:
    """ Function to register an already existing file from an external Google Drive. Requires the file to
    be 'readable by everyone with the link'.

    :return: tuple containing a JSON response and a status code
    """
    required_fields: list[str] = ['file_id']
    try:
        for field in required_fields:
            if field not in request.json or request.json[field] == "":
                raise ValueError(f'Field {field} is required.')

        file_id: str = request.json['file_id']
        connector: GoogleDriveConnector = GoogleDriveConnector()
        filename: str | None = connector.get_filename(file_id)
        if not filename:
            raise ValueError(f"File '{file_id}' does not exist.")

        filepath: str = connector.download_file(file_id, filename)

        extra_data: dict | None = extract_data_from_spreadsheet(filepath)
        if extra_data is None:
            raise ValueError(f"File '{file_id}' does not contain the required data.")

        batch: str = extra_data['batch']
        species: str = extra_data['organism_name']
        batch_used: File | None = get_shipped_file(species, batch)

        if batch_used:
            new_batch: str = request.json.get('new_batch', None)
            new_filename: tuple[Response, int] | str = change_batch(new_batch, species, filepath, filename)
            if isinstance(new_filename, tuple):
                return new_filename
            filename = new_filename
            extra_data['batch'] = new_batch

        organisation: Organisation = (Organisation.query
                                      .filter(Organisation.name == extra_data['organisation_name'])
                                      .first())
        del extra_data['organisation_name']

        file_data: dict[str, str] | None = connector.upload_file(organisation.gdrive_id, filepath, filename)
        remove(filepath)
        if not file_data:
            raise ValueError(f"File '{file_id}' could not be uploaded.")  # TODO: Test this

        file: File = File(gdrive_id=file_data['id'],
                          name=filename,
                          organisation_name=organisation.name,
                          user_id=get_current_user().id,
                          **extra_data)
        session.add(file)
        session.commit()
        msg: str = f'file {file_id} was successfully created with internal id {file.file_id}'
        return jsonify({"message": msg, "file": dict(file)}), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        LOGGER.error("Registration error: %s" % (str(e)))
        return jsonify({"message": 'An unexpected error occurred.'}), 500


def change_batch(new_batch: str, species: str, filepath: str, filename: str) -> tuple[Response, int] | str:
    """ Function to change the batch of a file if the batch is already used.

    :param new_batch: new batch to use
    :param species: species of the file
    :param filepath: path to the file
    :param filename: name of the file
    :return: new filename if the batch was changed, otherwise a tuple containing a JSON response and a status code
    """
    if not new_batch:
        remove(filepath)
        return jsonify({"message": f"Batch already used with {species}"}), 412
    else:
        if get_shipped_file(species, new_batch):
            remove(filepath)
            return jsonify({"message": f"Batch already used with {species}"}), 412
    batch_updater: BatchUpdater = BatchUpdater(batch=new_batch, filepath=filepath)
    filename = filename.replace(batch_updater.old_batch, new_batch)
    return filename
