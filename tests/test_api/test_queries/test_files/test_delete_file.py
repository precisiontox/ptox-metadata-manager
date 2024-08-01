from unittest import TestCase
from unittest.mock import patch

from ptmd.api import app
from ptmd.database.models import File


HEADERS = {'Content-Type': 'application/json', 'Authorization': 'Bearer 123'}


@patch('ptmd.api.queries.utils.get_current_user')
@patch('ptmd.api.queries.utils.verify_jwt_in_request')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
class TestDeleteFile(TestCase):

    @patch('ptmd.api.queries.files.delete.File')
    def test_delete_success(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        mock_file.query.filter().first.return_value = mock_file
        mock_file.received = False
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.delete('/api/files/1', headers=HEADERS)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'message': 'File 1 was successfully deleted.'})

    @patch('ptmd.api.queries.files.delete.File')
    def test_delete_not_allowed(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        mock_file.query.filter().first.return_value = mock_file
        mock_file.received = True
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.delete('/api/files/1', headers=HEADERS)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json, {'message': 'File 1 is marked as received and cannot be deleted.'})

    @patch('ptmd.api.queries.files.delete.File')
    def test_delete_error_404(self,  mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        mock_file.query.filter().first.return_value = None
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.delete('/api/files/1', headers=HEADERS)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {'message': 'File 1 does not exist.'})

    @patch('ptmd.api.queries.files.delete.File')
    def test_delete_error_403(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        msg = 'You do not have permission to perform this action.'
        mock_file.query.filter().first.return_value = mock_file
        mock_file.received = False
        mock_file.remove.side_effect = PermissionError(msg)
        #mock_file.query.filter().first().remove.side_effect = PermissionError(msg)
        mock_user().id = 1
        mock_user().role = 'user'
        with app.test_client() as client:
            response = client.delete('/api/files/1', headers=HEADERS)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.json, {'message': 'You do not have permission to perform this action.'})
