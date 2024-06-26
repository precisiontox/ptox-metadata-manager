""" ISA-Tab conversion endpoint
"""

from flask import jsonify, Response

from ptmd.logger import LOGGER
from ptmd.lib.isa import convert_file_to_isa
from ptmd.api.queries.utils import check_role


@check_role('admin')
def convert_to_isa(file_id: int) -> tuple[Response, int]:
    """ Method to convert a file to ISA-Tab

    :param file_id: the id of the file to convert
    :return: a tuple containing the response and the status code
    """
    try:
        response: dict = convert_file_to_isa(file_id)[0]
    except ValueError as e:
        LOGGER.error("ValueError: %s" % (str(e)))
        return jsonify({'message': 'File conversion failed.'}), 400
    except FileNotFoundError as e:
        LOGGER.error("File not found: %s" % (str(e)))
        return jsonify({'message': 'File not found.'}), 404
    return jsonify(response), 200
