from unittest import TestCase
from unittest.mock import patch

from ptmd.api import app


HEADERS = {'Content-Type': 'application/json'}


@patch('ptmd.api.queries.files.update.jsonify')
@patch('ptmd.api.queries.utils.get_current_user')
@patch('ptmd.api.queries.utils.verify_jwt_in_request')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
class TestUpdater(TestCase):

    def test_error_400(self, mock_jwt, mock_verify_jwt_in_request, mock_user, mock_jsonify):
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/1/batch', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.status_code, 400)
            mock_jsonify.assert_called_once_with({'message': 'No batch given'})

    def test_error_other(self, mock_jwt, mock_verify_jwt_in_request, mock_user, mock_jsonify):
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/1/batch?batch=AA', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.json,
                             {'message': 'Could not update: the new batch and old batch have the same value'})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.files.update.BatchUpdater')
    def test_success(self, moc_batch_updater, mock_jwt, mock_verify_jwt_in_request, mock_user, mock_jsonify):
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/1/batch?batch=AA', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.status_code, 200)
            mock_jsonify.assert_called_once_with({"message": "Batch updated"})
