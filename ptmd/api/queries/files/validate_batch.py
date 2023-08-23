from __future__ import annotations

from flask import request, Response, jsonify

from ptmd.api.queries.utils import check_role
from ptmd.database import File, Organism


@check_role('user')
def batch_validation(batch: str) -> tuple[Response, int]:
    """ This function verify that the given batch is not already used for this species
    """
    species: str | None = request.args.get('species', None)
    if not species:
        return jsonify({"message": "No species given"}), 400
    file: File | None = get_shipped_file(species, batch)
    if file:
        return jsonify({"message": f"Batch already used with {species}"}), 400
    return jsonify({"message": "Batch not used"}), 200


def get_shipped_file(species: str, batch: str) -> File | None:
    """ This function return the first received file with the given batch and species if it exists or None

    :param species: the species of the file
    :param batch: the batch of the file
    :return: the first received file with the given batch and species if it exists or None
    """
    return File.query.join(Organism).filter(
            Organism.ptox_biosystem_name == species,
            File.batch == batch,
            File.received != 0
    ).first()
