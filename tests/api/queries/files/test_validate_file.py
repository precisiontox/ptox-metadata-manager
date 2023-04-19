from unittest import TestCase
from unittest.mock import patch

from ptmd.api import app
from ptmd.api.queries.files.validate import validate_file


HEADERS = {'Content-Type': 'application/json'}


class MockedValidator:
    def __init__(self, file_id):
        self.report = {'valid': True, 'errors': []}

    def validate(self):
        pass


class MockedValidatorError:
    def __init__(self, file_id):
        self.report = {'valid': False, 'errors': ['error']}

    def validate(self):
        pass


class TestValidateFile(TestCase):

    @patch('ptmd.api.queries.files.validate.ExcelValidator', return_value=MockedValidator(1))
    def test_valid(self, mock_validator):
        report, code = validate_file(1)
        self.assertTrue(report['message'], "File validated successfully.")
        self.assertEqual(code, 200)

    @patch('ptmd.api.queries.files.validate.ExcelValidator', return_value=MockedValidatorError(1))
    @patch('ptmd.api.queries.files.validate.ExternalExcelValidator', return_value=MockedValidatorError(1))
    def test_error_406(self, mock_validator, mock_validator_ext):
        report, code = validate_file(1)
        self.assertEqual(report['message'], 'File validation failed.')
        self.assertEqual(code, 406)

        report, code = validate_file('a')
        self.assertEqual(report['errors'][0], 'error')
        self.assertEqual(code, 406)

        report, code = validate_file([1])
        self.assertIn("int() argument must be a string", report['error'])

    def test_error_404(self):
        report, code = validate_file(10)
        self.assertEqual(report['error'], 'File with ID 10 does not exist.')
        self.assertEqual(code, 404)

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.routes.validate_file', return_value=({'message': 'File validated successfully.'}, 200))
    def test_route(self, mock_validate, mock_jwt_required):
        with app.test_client() as test_client:
            response = test_client.get('/api/file/1/validate')
        self.assertEqual(response.json, {'message': 'File validated successfully.'})