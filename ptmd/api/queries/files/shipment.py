""" Methods to ship and receive the samples

@author: D. Batista (Terazus)
"""
from flask import jsonify, Response, request

from ptmd.database.models import File
from ptmd.api.queries.utils import check_role
from ptmd.lib.gdrive import GoogleDriveConnector
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
    file: File = File.query.filter_by(file_id=file_id).first()
    if not file:
        return jsonify({'message': f'File {file_id} not found.'}), 404
    try:
        file.ship_samples(at=request.json.get('at', None))
        connector: GoogleDriveConnector = GoogleDriveConnector()
        connector.lock_file(file.gdrive_id)
        return jsonify({'message': f'File {file_id} shipped successfully.'}), 200
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
    file: File = File.query.filter_by(file_id=file_id).first()
    if not file:
        return jsonify({'message': f'File {file_id} not found.'}), 404
    try:
        file.shipment_was_received(at=request.json.get('at', None))
        save_samples(file_id)
        return jsonify({'message': f'File {file_id} received successfully.'}), 200
    except PermissionError as e:
        return jsonify({'message': str(e)}), 403
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
