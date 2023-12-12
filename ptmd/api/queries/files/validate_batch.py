""" This module contains the route to validate a batch """
from __future__ import annotations

from flask import request, Response, jsonify

from ptmd.api.queries.utils import check_role
from ptmd.database import File, get_shipped_file


@check_role('user')
def batch_validation(batch: str) -> tuple[Response, int]:
    """ This function verify that the given batch is not already used for this species

    :param batch: The batch to verify
    :return: A tuple with the response and the status code
    """
    species: str | None = request.args.get('species', None)
    if not species:
        return jsonify({"message": "No species given"}), 400
    file: File | None = get_shipped_file(species, batch)
    if file:
        return jsonify({"message": f"Batch already used with {species}"}), 400
    return jsonify({"message": "Batch not used"}), 200
