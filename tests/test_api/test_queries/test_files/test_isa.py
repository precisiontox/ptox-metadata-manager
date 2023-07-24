from unittest import TestCase
from unittest.mock import patch

from ptmd.api import app


HEADERS = {'Content-Type': 'application/json', 'Authorization': 'Bearer 123'}


@patch('ptmd.api.queries.utils.get_current_user')
@patch('ptmd.api.queries.utils.verify_jwt_in_request')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
class TestISA(TestCase):

    def test_convert_error_404(self, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        mock_user().id = 1
        mock_user().role = 'admin'
        with patch('ptmd.api.queries.files.isa.convert_file_to_isa') as mock_convert:
            mock_convert.side_effect = FileNotFoundError('File not found.')
            with app.test_client() as client:
                response = client.get('/api/files/1/isa', headers=HEADERS)
                self.assertEqual(response.json, {'message': 'File not found.'})
                self.assertEqual(response.status_code, 404)

    def test_convert_error_400(self, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        mock_user().id = 1
        mock_user().role = 'admin'
        with patch('ptmd.api.queries.files.isa.convert_file_to_isa') as mock_convert:
            mock_convert.side_effect = ValueError('A 400 error.')
            with app.test_client() as client:
                response = client.get('/api/files/1/isa', headers=HEADERS)
                self.assertEqual(response.json, {'message': 'A 400 error.'})
                self.assertEqual(response.status_code, 400)

    def test_convert_success(self, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        mock_user().id = 1
        mock_user().role = 'admin'
        with patch('ptmd.api.queries.files.isa.convert_file_to_isa') as mock_convert:
            mock_convert.return_value = {'message': 'SUCCESS'}
            with app.test_client() as client:
                response = client.get('/api/files/1/isa', headers=HEADERS)
                self.assertEqual(response.json, {'message': 'SUCCESS'})
                self.assertEqual(response.status_code, 200)