""" This file handles the route that validates a google drive file.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from flask import jsonify, Response

from ptmd.lib.validator import ExcelValidator, ExternalExcelValidator
from ptmd.api.queries.utils import check_role


@check_role(role='user')
def validate_file(file_id: int | str) -> tuple[Response, int]:
    """ Method to validate the file in the Google Drive.

    :param file_id: the file id to validate
    :return: dictionary containing the response from the Google Drive API
    """
    validator: ExcelValidator

    try:
        validator = ExcelValidator(int(file_id))
    except (ValueError, TypeError):
        validator = ExternalExcelValidator(str(file_id))

    try:
        validator.validate()
        code: int = 200
        message: str = "File validated successfully."
        errors: list = []
        if not validator.report['valid']:
            code = 406
            message = "File validation failed."
            errors = validator.report['errors']
        return (
            jsonify({"message": message, "id": file_id, "errors": errors, 'gdrive': validator.file['gdrive_id']}),
            code
        )
    except Exception as e:
        error: dict = e.__dict__
        error_msg = error['error']['errors'][0]['message'] if error else str(e)
        error_code = error['error']['code'] if error else 404
        return jsonify({"errors": error_msg}), error_code
