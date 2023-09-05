""" A module to handle the update of a file batch. """

from flask import request, Response, jsonify

from ptmd.api.queries.utils import check_role
from ptmd.lib import BatchUpdater, BatchError


@check_role(role='user')
def update_file_batch(file_id: int) -> tuple[Response, int]:
    """ Method to update the batch of a file

    :param file_id: the id of the file to be updated
    :return: a tuple with the response and the status code
    """
    batch = request.args.get('batch', None)

    if not batch:
        return jsonify({"message": "No batch given"}), 400

    try:
        BatchUpdater(batch=batch, file_id=file_id)
        return jsonify({"message": "Batch updated"}), 200
    except BatchError as error:
        return error.serialize()
