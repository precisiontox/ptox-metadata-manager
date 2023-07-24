""" ISA-Tab conversion endpoint

@author: D. Batista (Terazus)
"""

from flask import jsonify, Response

from ptmd.lib.isa import convert_file_to_isa
from ptmd.api.queries.utils import check_role


@check_role('admin')
def convert_to_isa(file_id: int) -> tuple[Response, int]:
    """ Method to convert a file to ISA-Tab

    :param file_id: the id of the file to convert
    :return: a tuple containing the response and the status code
    """
    try:
        response: list[dict] = convert_file_to_isa(file_id)
    except ValueError as e:
        return jsonify({'message': str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({'message': str(e)}), 404
    return jsonify(response), 200
