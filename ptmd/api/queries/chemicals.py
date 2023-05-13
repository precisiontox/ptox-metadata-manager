from typing import Generator
from json import load

from flask import jsonify, request, Response
from sqlalchemy.exc import IntegrityError
from jsonschema import Draft202012Validator as JSONValidator, RefResolver, ValidationError

from ptmd.const import CREATE_CHEMICAL_SCHEMA_PATH, CREATE_CHEMICALS_SCHEMA_PATH
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
        chemicals_from_db: list[Chemical] = [Chemical(**chemical) for chemical in chemicals]
        session.add_all(chemicals_from_db)
        session.commit()
        return jsonify({
            'message': 'Chemicals created successfully.',
            'data': [dict(chemical) for chemical in chemicals_from_db]
        }), 201
    except ValidationError as e:
        return jsonify({'message': e.message}), 400
    except IntegrityError:
        session.rollback()
        return jsonify({'message': "common_name and ptx_code must be uniques"}), 500


def validate_chemicals(chemicals: list[dict]) -> None:
    with open(CREATE_CHEMICAL_SCHEMA_PATH, 'r') as f:
        create_chemical_schema = load(f)
    with open(CREATE_CHEMICALS_SCHEMA_PATH, 'r') as f:
        create_chemicals_schema = load(f)
    schema_mapping: dict = {
        create_chemicals_schema['$id']: create_chemicals_schema,
        create_chemical_schema['$id']: create_chemical_schema
    }
    resolver: RefResolver = RefResolver(store=schema_mapping, base_uri='file:///', referrer=create_chemicals_schema)
    validator: JSONValidator = JSONValidator(create_chemicals_schema, resolver=resolver)
    errors: Generator = validator.iter_errors(chemicals)
    for error in errors:
        message: str = f"'{error.path[0]}' value {error.message}" if error.path else error.message
        raise ValidationError(message)