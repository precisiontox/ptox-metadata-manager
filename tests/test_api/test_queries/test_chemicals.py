from unittest import TestCase
from unittest.mock import patch
from json import dumps

from jsonschema import ValidationError
from sqlalchemy.exc import IntegrityError

from ptmd.api.queries.chemicals import validate_chemicals
from ptmd.api import app

VALID_CHEMICAL = {"common_name": 'test', "formula": 'test', 'ptx_code': "PTX780"}
INVALID_CHEMICAL = {"common_name": 'test', "formula": 'test'}
HEADERS = {'Content-Type': 'application/json'}


class TestAPIChemicals(TestCase):

    def test_validate_chemicals_errors(self):
        chemicals = []
        with self.assertRaises(ValidationError) as context:
            validate_chemicals(chemicals)
        self.assertEqual(str(context.exception), "[] is too short")

        chemicals = [{"common_name": 'test'}]
        with self.assertRaises(ValidationError) as context:
            validate_chemicals(chemicals)
        self.assertEqual(str(context.exception), "'0' value 'formula' is a required property")

        chemicals = [{"common_name": 'test', "formula": 'test', 'ptx_code': 'test'}]
        with self.assertRaises(ValidationError) as context:
            validate_chemicals(chemicals)
        self.assertEqual(str(context.exception), "'0' value 'test' does not match '^PTX[0-9]{3}?$'")

    def test_validate_chemicals_success(self):
        self.assertIsNone(validate_chemicals([VALID_CHEMICAL]))

    @patch('ptmd.api.queries.chemicals.session')
    @patch('ptmd.api.queries.utils.verify_jwt_in_request', return_value=None)
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user')
    @patch('ptmd.api.queries.utils.check_role')
    @patch('ptmd.api.queries.chemicals.Chemical')
    def test_create_chemicals_success(self, mock_chemical, mock_role, mock_get_current_user,
                                      mock_verify_jwt, mock_verify_in_request, mock_get_session):
        mock_get_current_user.return_value.role = 'user'
        mock_chemical.return_value.chemical_id = 1
        with app.test_client() as client:
            response = client.post('/api/chemicals',
                                   headers={'Authorization': f'Bearer {123}', **HEADERS},
                                   data=dumps({'chemicals': [VALID_CHEMICAL]}))
            self.assertEqual(response.json, {'data': [1], 'message': 'Chemicals created successfully.'})
            self.assertEqual(response.status_code, 201)

    @patch('ptmd.api.queries.utils.verify_jwt_in_request', return_value=None)
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user')
    @patch('ptmd.api.queries.utils.check_role')
    def test_create_chemicals_error(self, mock_role, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        mock_get_current_user.return_value.role = 'user'
        with app.test_client() as client:
            response = client.post('/api/chemicals',
                                   headers={'Authorization': f'Bearer {123}', **HEADERS},
                                   data=dumps({'chemicals': [INVALID_CHEMICAL]}))
            self.assertEqual("'0' value 'ptx_code' is a required property", response.json['message'])
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.chemicals.session')
    @patch('ptmd.api.queries.utils.verify_jwt_in_request', return_value=None)
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user')
    @patch('ptmd.api.queries.utils.check_role')
    @patch('ptmd.api.queries.chemicals.Chemical')
    def test_create_chemicals_errors_integrity(self, mock_chemical, mock_role, mock_get_current_user,
                                               mock_verify_jwt, mock_verify_in_request, mock_get_session):
        mock_get_current_user.return_value.role = 'user'
        mock_chemical.return_value = MockChemical()
        mock_get_session.add_all.side_effect = IntegrityError(None, None, None)
        with app.test_client() as client:
            response = client.post('/api/chemicals',
                                   headers={'Authorization': f'Bearer {123}', **HEADERS},
                                   data=dumps({'chemicals': [VALID_CHEMICAL]}))
            self.assertEqual(response.status_code, 500)
            self.assertEqual(response.json, {'message': "common_name and ptx_code must be uniques"})
