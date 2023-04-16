""" This file handles the route that validates a google drive file.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from ptmd.clients.validator import ExcelValidator


def validate_file(file_id: int | str):
    """ Method to validate the file in the Google Drive.

    :param file_id: the file id to validate
    :return: dictionary containing the response from the Google Drive API
    """
    try:
        file_id = int(file_id)
    except ValueError:
        return {"error": "File ID must be an integer."}, 400

    try:
        validator = ExcelValidator(file_id)
        code: int = 200
        message: str = "File validated successfully."
        errors: list = []
        if not validator.report['valid']:
            code = 400
            message = "File validation failed."
            errors = validator.report['errors']
        return {"message": message, "id": file_id, "errors": errors}, code
    except ValueError as e:
        return {"error": str(e)}, 404
