from unittest import TestCase
from unittest.mock import patch

from ptmd.api import app


HEADERS = {'Content-Type': 'application/json', 'Authorization': 'Bearer 123'}


@patch('ptmd.api.queries.utils.get_current_user')
@patch('ptmd.api.queries.utils.verify_jwt_in_request')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
class TestShipments(TestCase):

    @patch('ptmd.api.queries.files.shipment.File')
    def test_ship_error_404(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        mock_file.query.filter_by().first.return_value = None
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/1/ship', headers=HEADERS)
            self.assertEqual(response.json, {'message': 'File 1 not found.'})
            self.assertEqual(response.status_code, 404)

    @patch('ptmd.api.queries.files.shipment.File')
    def test_ship_error_403(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class FileMock:
            def ship_samples(self):
                raise PermissionError('You do not have permission to perform this action.')

        mock_file.query.filter_by().first.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/1/ship', headers=HEADERS)
            self.assertEqual(response.json, {'message': 'You do not have permission to perform this action.'})
            self.assertEqual(response.status_code, 403)

    @patch('ptmd.api.queries.files.shipment.File')
    def test_ship_error_400(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class FileMock:
            def ship_samples(self):
                raise ValueError('A value error.')

        mock_file.query.filter_by().first.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/1/ship', headers=HEADERS)
            self.assertEqual(response.json, {'message': 'A value error.'})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.files.shipment.File')
    @patch('ptmd.api.queries.files.shipment.GoogleDriveConnector')
    def test_ship_success(self, mock_drive, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class FileMock:
            def __init__(self):
                self.gdrive_id = '123'

            def ship_samples(self):
                pass
        mock_file.query.filter_by().first.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/1/ship', headers=HEADERS)
            self.assertEqual(response.json, {'message': f'File 1 shipped successfully.'})
            self.assertEqual(response.status_code, 200)
            mock_drive().lock_file.assert_called_once_with('123')

    @patch('ptmd.api.queries.files.shipment.File')
    def test_receive_data_error_404(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        mock_file.query.filter_by().first.return_value = None
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/1/receive', headers=HEADERS)
            self.assertEqual(response.json, {'message': 'File 1 not found.'})
            self.assertEqual(response.status_code, 404)

    @patch('ptmd.api.queries.files.shipment.File')
    def test_receive_data_error_403(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class FileMock:
            def shipment_was_received(self):
                raise PermissionError('You do not have permission to perform this action.')

        mock_file.query.filter_by().first.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/1/receive', headers=HEADERS)
            self.assertEqual(response.json, {'message': 'You do not have permission to perform this action.'})
            self.assertEqual(response.status_code, 403)

    @patch('ptmd.api.queries.files.shipment.File')
    def test_receive_data_error_400(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class FileMock:
            def shipment_was_received(self):
                raise ValueError('A value error.')

        mock_file.query.filter_by().first.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/1/receive', headers=HEADERS)
            self.assertEqual(response.json, {'message': 'A value error.'})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.files.shipment.File')
    @patch('ptmd.api.queries.files.shipment.save_samples')
    def test_receive_data_success(self, mock_save, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class FileMock:
            def __init__(self):
                self.gdrive_id = '123'

            def shipment_was_received(self):
                pass
        mock_file.query.filter_by().first.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/1/receive', headers=HEADERS)
            self.assertEqual(response.json, {'message': f'File 1 received successfully.'})
            self.assertEqual(response.status_code, 200)
            mock_save.assert_called_once_with("1")

