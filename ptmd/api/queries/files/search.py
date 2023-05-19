""" This module contains the endpoint for searching for files in the database

@author: D. Batista (Terazus)
"""

from __future__ import annotations

from werkzeug.datastructures import ImmutableMultiDict
from flask import jsonify, Response, request

from ptmd.database.queries import search_files
from ptmd.api.queries.utils import check_role


@check_role(role='user')
def search_files_in_database() -> tuple[Response, int]:
    """ Search for files in the database

    :return: a response with the files found in the database and the pagination information
    """
    page: int = request.args.get('page', 1, type=int)
    per_page: int = request.args.get('per_page', 10, type=int)
    valid: bool | None = get_state_input(request.args)
    organisation_name: str | None = request.args.get('organisation', None, type=str)
    organism_name: str | None = request.args.get('organism', None, type=str)
    vehicle_name: str | None = request.args.get('vehicle', None, type=str)
    chemical_name: str | None = request.args.get('chemical', None, type=str)
    replicates: dict | None = get_integer_input(request.args, 'replicates')
    controls: dict | None = get_integer_input(request.args, 'controls')
    blanks: dict | None = get_integer_input(request.args, 'blanks')
    response: dict = search_files(page=page, per_page=per_page, is_valid=valid,
                                  organisation_name=organisation_name, organism_name=organism_name,
                                  vehicle_name=vehicle_name, chemical_name=chemical_name,
                                  replicates=replicates, controls=controls, blanks=blanks)
    if len(response['data']) == 0:
        return jsonify({"message": "No files found"}), 404
    return jsonify(response), 200


def get_state_input(args: ImmutableMultiDict) -> bool | None:
    """ Get the state of the file as a boolean given its string representation

    :param args: the arguments passed in the request
    :return: the state of the file as a boolean or None if the state is not specified
    """
    true_values: list = ['true', 'True', '1', 1]
    false_values: list = ['false', 'False', '0', 0]
    if 'valid' not in args:
        return None
    return True if args['valid'] in true_values else False if args['valid'] in false_values else None


def get_integer_input(args: ImmutableMultiDict, field: str) -> dict | None:
    """ Get the integer input from the request arguments for the given field

    :param args: the arguments passed from the request
    :param field: the field to get the input for
    """
    operator_field: str = f'{field}_operator'
    value: int | None = args.get(field, None, type=int)
    operator: str | None = args.get(operator_field, None, type=str)
    if not value:
        return None
    elif not operator:
        return {'value': value, 'operator': 'eq'}
    else:
        if operator not in ['eq', 'lt', 'gt', 'lte', 'gte', 'ne']:
            return {'value': value, 'operator': 'eq'}
        return {'value': value, 'operator': operator}
