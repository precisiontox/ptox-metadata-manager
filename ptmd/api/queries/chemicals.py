""" This module contains queries for chemicals.
"""

from typing import Generator
from json import load

from flask import jsonify, request, Response
from sqlalchemy.exc import IntegrityError
from jsonschema import Draft4Validator as JSONValidator, RefResolver, ValidationError

from ptmd.const import CREATE_CHEMICAL_SCHEMA_PATH, CREATE_CHEMICALS_SCHEMA_PATH, BASE_IDENTIFIER
from ptmd.config import session
from ptmd.api.queries.utils import check_role
from ptmd.database.models import Chemical


@check_role(role='user')
def create_chemicals() -> tuple[Response, int]:
    """ Create new chemicals from payload.

    :return: tuple of response and status code
    """
    chemicals: list = request.json.get('chemicals', None)
    try:
        validate_chemicals(chemicals)
        for chemical in chemicals:
            chemical['ptx_code'] = int(chemical['ptx_code'].replace(BASE_IDENTIFIER, ''))
        chemicals_from_db: list[Chemical] = [Chemical(**chemical) for chemical in chemicals]
        session.add_all(chemicals_from_db)
        session.commit()
        return jsonify({
            'message': 'Chemicals created successfully.',
            'data': [chemical.chemical_id for chemical in chemicals_from_db]
        }), 201
    except ValidationError as e:
        return jsonify({'message': e.message}), 400
    except IntegrityError:
        session.rollback()
        return jsonify({'message': "common_name and ptx_code must be uniques"}), 500


def validate_chemicals(chemicals: list[dict]) -> None:
    """ Validate chemicals against schema.

    :param chemicals: list of chemicals
    :exception ValidationError: if validation fails
    """
    with open(CREATE_CHEMICAL_SCHEMA_PATH, 'r') as f:
        create_chemical_schema = load(f)
    with open(CREATE_CHEMICALS_SCHEMA_PATH, 'r') as f:
        create_chemicals_schema = load(f)
    schema_mapping: dict = {
        create_chemicals_schema['$id']: create_chemicals_schema,
        create_chemical_schema['$id']: create_chemical_schema,
        'file:///create_chemicals_schema.json': create_chemicals_schema,
        'file:///create_chemical_schema.json': create_chemical_schema
    }
    resolver: RefResolver = RefResolver(store=schema_mapping, base_uri='file:///', referrer=create_chemicals_schema)
    validator: JSONValidator = JSONValidator(create_chemicals_schema, resolver=resolver)
    errors: Generator = validator.iter_errors(chemicals)
    for error in errors:
        message: str = f"'{error.path[0]}' value {error.message}" if error.path else error.message
        raise ValidationError(message)


def get_chemical(ptx_code: str) -> tuple[Response, int]:
    """ Get chemical by its ptx_code.

    :param ptx_code: the ptx_code of the chemical
    :return: tuple of response and status code
    """
    chemical_id = int(ptx_code.replace(BASE_IDENTIFIER, ''))
    chemical: Chemical = Chemical.query.filter(Chemical.ptx_code == chemical_id).first()
    if not chemical:
        return jsonify({'message': 'Chemical not found.'}), 404
    return jsonify(msg=dict(chemical)), 200
