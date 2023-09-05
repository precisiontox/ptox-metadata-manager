from unittest import TestCase
from unittest.mock import patch

from ptmd.api import app
from ptmd.api.queries.files.validate import validate_file


HEADERS = {'Content-Type': 'application/json'}


class MockedValidator:
    def __init__(self, file_id):
        self.report = {'valid': True, 'errors': []}
        self.file = {'gdrive_id': file_id}

    def validate(self):
        pass


class MockedValidatorFailed:
    def __init__(self, file_id):
        self.report = {'valid': False, 'errors': ['error']}
        self.file = {'gdrive_id': file_id}

    def validate(self):
        pass


class CustomException(Exception):
    def __init__(self, error):
        self.__dict__ = {
            'error': {
                'errors': [{'message': error}],
                'code': 404
            }
        }


class MockedValidatorError(MockedValidator):
    def validate(self):
        raise CustomException('test')


class TestValidateFile(TestCase):

    @patch('ptmd.api.queries.files.validate.ExcelValidator', return_value=MockedValidator(1))
    @patch('ptmd.api.queries.utils.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user', return_value=MockedValidatorError(1))
    @patch('ptmd.api.queries.files.validate.jsonify', return_value='success')
    def test_valid(self, mock_jsonify, mock_get_current_user, mock_jwt, mock_validator):
        mock_get_current_user().role = 'user'
        report, code = validate_file(1)
        self.assertTrue(report, "success")
        self.assertEqual(code, 200)

    @patch('ptmd.api.queries.files.validate.ExcelValidator', return_value=MockedValidatorFailed(1))
    @patch('ptmd.api.queries.files.validate.ExternalExcelValidator', return_value=MockedValidatorFailed(1))
    @patch('ptmd.api.queries.utils.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user', return_value=MockedValidatorError(1))
    @patch('ptmd.api.queries.files.validate.jsonify', return_value='File validation failed.')
    def test_error_406(self, mock_jsonify, mock_get_current_user, mock_jwt, mock_validator, mock_external_validator):
        mock_get_current_user().role = 'user'
        report, code = validate_file(1)
        self.assertEqual(report, 'File validation failed.')
        self.assertEqual(code, 406)
        report, code = validate_file('a')
        self.assertEqual(report, 'File validation failed.')
        self.assertEqual(code, 406)

    @patch('ptmd.api.queries.files.validate.ExcelValidator', return_value=MockedValidatorError(1))
    @patch('ptmd.api.queries.utils.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user', return_value=MockedValidatorError(1))
    @patch('ptmd.api.queries.files.validate.jsonify', return_value={'error': 'test'})
    def test_error_404(self, mock_jsonify, mock_get_current_user, mock_jwt, mock_validator):
        mock_get_current_user().role = 'user'
        report, code = validate_file(1)
        self.assertTrue(report['error'], "test")
        self.assertEqual(code, 404)

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.routes.validate_file', return_value=({'message': 'File validated successfully.'}, 200))
    def test_route(self, mock_validate, mock_jwt_required):
        with app.test_client() as test_client:
            response = test_client.get('/api/files/1/validate')
        self.assertEqual(response.json, {'message': 'File validated successfully.'})
