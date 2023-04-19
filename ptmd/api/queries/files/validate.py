""" This file handles the route that validates a google drive file.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from ptmd.lib.validator import ExcelValidator, ExternalExcelValidator


def validate_file(file_id: int | str):
    """ Method to validate the file in the Google Drive.

    :param file_id: the file id to validate
    :return: dictionary containing the response from the Google Drive API
    """
    validator: ExcelValidator

    try:
        validator = ExcelValidator(int(file_id))
    except Exception as e:
        if isinstance(file_id, str):
            validator = ExternalExcelValidator(file_id)
        else:
            return {"error": str(e)}, 404

    try:
        validator.validate()
        code: int = 200
        message: str = "File validated successfully."
        errors: list = []
        if not validator.report['valid']:
            code = 406
            message = "File validation failed."
            errors = validator.report['errors']
        return {"message": message, "id": file_id, "errors": errors}, code
    except Exception as e:
        return {"error": str(e)}, 404
