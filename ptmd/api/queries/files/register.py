""" Module to register an already existing file from an external Google Drive. Requires the file to
be 'readable by everyone with the link'. Will create an entry in the database.

@author: D. Batista (Terazus)
"""

from __future__ import annotations

from re import match

from flask import jsonify, Response, request
from flask_jwt_extended import get_jwt

from ptmd.config import session
from ptmd.const import ALLOWED_EXPOSURE_BATCH
from ptmd.database import Organisation, File, User
from ptmd.lib.gdrive import GoogleDriveConnector
from ptmd.api.queries.utils import check_role


@check_role(role='enabled')
def register_gdrive_file() -> tuple[Response, int]:
    """ Function to register an already existing file from an external Google Drive. Requires the file to
    be 'readable by everyone with the link'.

    :return: tuple containing a JSON response and a status code
    """
    required_fields: list[str] = ['file_id', 'batch', 'organism']
    try:
        for field in required_fields:
            if field not in request.json or request.json[field] == "":
                raise ValueError(f'Field {field} is required.')

        file_id: str = request.json['file_id']
        user_id: int = get_jwt()['sub']
        batch: str = request.json['batch']
        user: User = User.query.filter(User.id == user_id).first()
        organisation: Organisation = user.organisation

        connector: GoogleDriveConnector = GoogleDriveConnector()
        if not match(ALLOWED_EXPOSURE_BATCH, batch):
            raise ValueError(f"Batch '{batch}' has an incorrect format.")

        filename: str | None = connector.get_filename(file_id)
        if not filename:
            raise ValueError(f"File '{file_id}' does not exist.")

        file: File = File(gdrive_id=file_id,
                          batch=batch,
                          organism_name=request.json['organism'],
                          name=filename,
                          organisation_name=organisation.name,
                          user_id=user_id)
        session.add(file)
        session.commit()
        msg: str = f'file {file_id} was successfully created with internal id {file.file_id}'
        return jsonify({"data": {"message": msg, "file_url": file.file_id}}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
