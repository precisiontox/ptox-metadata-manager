""" This module contains the endpoint to delete files
"""

from flask import jsonify, Response

from ptmd.logger import LOGGER
from ptmd.database.models import File
from ptmd.api.queries.utils import check_role


@check_role('enabled')
def delete_file(file_id: int) -> tuple[Response, int]:
    """ Given a file id, deletes the record from the database if the user has the required permissions. The user
    must be the owner of the file or an admin.

    :param file_id: the id of the file to be deleted
    :return: A tuple containing a JSON response and a status code
    """
    file: File = File.query.filter(File.file_id == file_id).first()
    if file is None:
        return jsonify({"message": f"File {file_id} does not exist."}), 404

    if file.received:
        return jsonify({"message": f"File {file_id} is marked as received and cannot be deleted."}), 403

    try:
        file.remove()
        return jsonify({"message": f"File {file_id} was successfully deleted."}), 200
    except PermissionError as e:
        LOGGER.error("Permission Error: %s" % (str(e)))
        return jsonify({"message": 'You do not have permission to perform this action.'}), 403
