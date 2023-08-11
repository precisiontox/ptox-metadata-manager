""" Module to register an already existing file from an external Google Drive. Requires the file to
be 'readable by everyone with the link'. Will create an entry in the database.
"""
from __future__ import annotations

from os import remove
from uuid import uuid4

from flask import jsonify, Response, request
from flask_jwt_extended import get_current_user

from ptmd.config import session
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

        filepath: str = connector.download_file(file_id, filename.replace('.xlsx', f'_{uuid4()}.xlsx'))
        extra_data: dict | None = extract_data_from_spreadsheet(filepath)

        if extra_data is None:
            raise ValueError(f"File '{file_id}' does not contain the required data.")

        organisation: Organisation = (Organisation.query
                                      .filter(Organisation.name == extra_data['organisation_name'])
                                      .first())
        del extra_data['organisation_name']
        file_data: dict[str, str] | None = connector.upload_file(
            directory_id=organisation.gdrive_id, file_path=filepath, title=filename
        )
        remove(filepath)
        if not file_data:
            raise ValueError(f"File '{file_id}' could not be uploaded.")

        file: File = File(gdrive_id=file_data['id'],
                          name=filename,
                          organisation_name=organisation.name,
                          user_id=get_current_user().id,
                          **extra_data)
        session.add(file)
        session.commit()
        msg: str = f'file {file_id} was successfully created with internal id {file.file_id}'
        return jsonify({"message": msg, "file": dict(file)}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
