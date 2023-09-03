""" Methods to ship and receive the samples
"""
from __future__ import annotations

from flask import jsonify, Response, request

from ptmd.database import File, get_shipped_file
from ptmd.api.queries.utils import check_role
from ptmd.lib import GoogleDriveConnector, BatchUpdater, BatchError
from ptmd.api.queries.samples import save_samples


@check_role(role='user')
def ship_data(file_id: int) -> tuple[Response, int]:
    """ Method to ship the samples to UoB

    :param file_id: the id of the file to be shipped
    :return: a tuple with the response and the status code
    :exception PermissionError: if the user is not the owner of the file
    :exception ValueError: if the file is not in the correct state
    """
    # TODO: send an email to the admin when the samples are shipped
    try:
        new_batch: str | None = request.args.get('new_batch', None)
        file: File = validate_batch(file_id=file_id, new_batch=new_batch)
        file.ship_samples(at=request.json.get('at', None))
        connector: GoogleDriveConnector = GoogleDriveConnector()
        connector.lock_file(file.gdrive_id)
        return jsonify({'message': f'File {file_id} shipped successfully.'}), 200
    except BatchError as e:
        return e.serialize()
    except PermissionError:
        return jsonify({'message': f'File {file_id} could not be locked but has been sent anyway'}), 200
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


@check_role(role='user')
def receive_data(file_id: int) -> tuple[Response, int]:
    """ Method to receive the samples from UoB

    :param file_id: the id of the file to be received
    :return: a tuple with the response and the status code
    :exception PermissionError: if the user is not an admin
    :exception ValueError: if the file is not in the correct state
    """
    try:
        new_batch: str | None = request.args.get('new_batch', None)
        file: File = validate_batch(file_id, new_batch)
        file.shipment_was_received(at=request.json.get('at', None))
        save_samples(file_id)
        return jsonify({'message': f'File {file_id} received successfully.'}), 200
    except BatchError as e:
        return e.serialize()
    except PermissionError as e:
        return jsonify({'message': str(e)}), 403
    except ValueError as e:
        return jsonify({'message': str(e)}), 400


def validate_batch(file_id: int, new_batch: str | None = None) -> File:
    """ Function to verify if the batch is valid and automatically update the file if a valid new batch is provided

    :param file_id: the id of the file to be validated
    :param new_batch: the new batch to be used
    """
    file: File = File.query.filter_by(file_id=file_id).first()
    if not file:
        raise BatchError(f'File {file_id} not found.', 404)
    if not new_batch and get_shipped_file(file.organism.ptox_biosystem_name, file.batch):
        raise BatchError(f'Batch already used with {file.organism.ptox_biosystem_name}', 412)
    if new_batch:
        batch_updater: BatchUpdater = BatchUpdater(batch=new_batch, file_id=file_id)
        return batch_updater.file
    return file
