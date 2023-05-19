""" Module to register an already existing file from an external Google Drive. Requires the file to
be 'readable by everyone with the link'. Will create an entry in the database.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from os import remove
from re import match
from uuid import uuid4

from flask import jsonify, Response, request
from flask_jwt_extended import get_current_user

from ptmd.config import session
from ptmd.const import ALLOWED_EXPOSURE_BATCH
from ptmd.database import Organisation, File
from ptmd.lib.gdrive import GoogleDriveConnector
from ptmd.lib.data_extractor import extract_data_from_spreadsheet
from ptmd.api.queries.utils import check_role


@check_role(role='enabled')
def register_gdrive_file() -> tuple[Response, int]:
    """ Function to register an already existing file from an external Google Drive. Requires the file to
    be 'readable by everyone with the link'.

    :return: tuple containing a JSON response and a status code
    """
    required_fields: list[str] = ['file_id', 'batch', 'organism', 'partner']
    try:
        for field in required_fields:
            if field not in request.json or request.json[field] == "":
                raise ValueError(f'Field {field} is required.')

        batch: str = request.json['batch']
        if not match(ALLOWED_EXPOSURE_BATCH, batch):
            raise ValueError(f"Batch '{batch}' has an incorrect format.")

        file_id: str = request.json['file_id']
        connector: GoogleDriveConnector = GoogleDriveConnector()
        filename: str | None = connector.get_filename(file_id)
        if not filename:
            raise ValueError(f"File '{file_id}' does not exist.")

        filepath: str = connector.download_file(file_id, filename.replace('.xlsx', f'_{uuid4()}.xlsx'))
        extra_data: dict | None = extract_data_from_spreadsheet(filepath)
        remove(filepath)
        if extra_data is None:
            raise ValueError(f"File '{file_id}' does not contain the required data.")

        organisation: Organisation = Organisation.query.filter(Organisation.name == request.json['partner']).first()
        file: File = File(gdrive_id=file_id,
                          batch=batch,
                          organism_name=request.json['organism'],
                          name=filename,
                          organisation_name=organisation.name,
                          user_id=get_current_user().id,
                          **extra_data)
        session.add(file)
        session.commit()
        msg: str = f'file {file_id} was successfully created with internal id {file.file_id}'
        return jsonify({"data": {"message": msg, "file_url": file.file_id}}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
