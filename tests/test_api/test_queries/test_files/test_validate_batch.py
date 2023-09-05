from unittest import TestCase
from unittest.mock import patch

from ptmd.api import app


HEADERS = {'Content-Type': 'application/json'}


@patch('ptmd.api.queries.files.validate_batch.jsonify')
@patch('ptmd.api.queries.utils.get_current_user')
@patch('ptmd.api.queries.utils.verify_jwt_in_request')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
class TestUpdater(TestCase):

    def test_error_400(self, mock_jwt, mock_verify_jwt_in_request, mock_user, mock_jsonify):
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/batch/AA/validate', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.status_code, 400)
            mock_jsonify.assert_called_once_with({'message': 'No species given'})

    @patch('ptmd.api.queries.files.validate_batch.get_shipped_file', return_value=True)
    def test_error_batch_used(self, mock_shipped, mock_jwt, mock_verify_jwt_in_request, mock_user, mock_jsonify):
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/batch/AA/validate?species=Daphnia',
                                  headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.status_code, 400)
            mock_jsonify.assert_called_once_with({'message': 'Batch already used with Daphnia'})

    @patch('ptmd.api.queries.files.validate_batch.get_shipped_file', return_value=False)
    def test_success(self, mock_shipped, mock_jwt, mock_verify_jwt_in_request, mock_user, mock_jsonify):
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/batch/AA/validate?species=Daphnia',
                                  headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.status_code, 200)
            mock_jsonify.assert_called_once_with({'message': 'Batch not used'})
