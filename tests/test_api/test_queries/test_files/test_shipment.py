from unittest import TestCase
from unittest.mock import patch

from ptmd.api import app
from ptmd.api.queries.files.shipment import validate_batch
from ptmd.lib import BatchError

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
            response = client.post('/api/files/1/ship', headers=HEADERS, json={})
            self.assertEqual(response.json, {'message': 'File 1 not found.'})
            self.assertEqual(response.status_code, 404)

    @patch('ptmd.api.queries.files.shipment.validate_batch')
    def test_ship_error_403(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class FileMock:
            def ship_samples(self, at):
                raise PermissionError('You do not have permission to perform this action.')

        mock_file.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.post('/api/files/1/ship', headers=HEADERS, json={})
            self.assertEqual(response.json, {'message': 'File 1 could not be locked but has been sent anyway'})
            self.assertEqual(response.status_code, 200)

    @patch('ptmd.api.queries.files.shipment.validate_batch')
    def test_ship_error_400(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class FileMock:
            def ship_samples(self, at):
                raise ValueError('A value error.')
        mock_file.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.post('/api/files/1/ship', headers=HEADERS, json={})
            self.assertEqual(response.json, {'message': 'A value error.'})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.files.shipment.validate_batch')
    @patch('ptmd.api.queries.files.shipment.GoogleDriveConnector')
    @patch('ptmd.api.queries.files.shipment.email_admins_file_shipped')
    @patch('ptmd.api.queries.files.shipment.session')
    def test_ship_error_500(
        self,
        mock_session,
        mock_ship,
        mock_drive,
        mock_file,
        mock_jwt_verify_flask,
        mock_jwt_verify_utils,
        mock_user
    ):
        class FileMock:
            def __init__(self):
                self.gdrive_id = '123'

            def ship_samples(self, at):
                pass
        mock_file.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        mock_ship.side_effect = Exception()
        with app.test_client() as client:
            response = client.post('/api/files/1/ship', headers=HEADERS, json={})
            self.assertEqual(response.status_code, 500)
            mock_session.rollback.assert_called_once()

    @patch('ptmd.api.queries.files.shipment.validate_batch')
    @patch('ptmd.api.queries.files.shipment.GoogleDriveConnector')
    @patch('ptmd.api.queries.files.shipment.email_admins_file_shipped')
    def test_ship_success(
            self,
            mock_ship,
            mock_drive,
            mock_file,
            mock_jwt_verify_flask,
            mock_jwt_verify_utils,
            mock_user
    ):
        class FileMock:
            def __init__(self):
                self.gdrive_id = '123'

            def ship_samples(self, at):
                pass

        mock_file.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.post('/api/files/1/ship', headers=HEADERS, json={})
            self.assertEqual(response.json, {'message': 'File 1 shipped successfully.'})
            self.assertEqual(response.status_code, 200)
            mock_drive().lock_file.assert_called_once_with('123')
            mock_ship.assert_called_once_with('1')

    @patch('ptmd.api.queries.files.shipment.File')
    def test_receive_data_error_404(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        mock_file.query.filter_by().first.return_value = None
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.post('/api/files/1/receive', headers=HEADERS, json={})
            self.assertEqual(response.json, {'message': 'File 1 not found.'})
            self.assertEqual(response.status_code, 404)

    @patch('ptmd.api.queries.files.shipment.validate_batch')
    def test_receive_data_error_403(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class FileMock:
            def shipment_was_received(self, at):
                raise PermissionError('You do not have permission to perform this action.')

        mock_file.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.post('/api/files/1/receive', headers=HEADERS, json={})
            self.assertEqual(response.json, {'message': 'You do not have permission to perform this action.'})
            self.assertEqual(response.status_code, 403)

    @patch('ptmd.api.queries.files.shipment.validate_batch')
    def test_receive_data_error_400(self, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class FileMock:
            def shipment_was_received(self, at):
                raise ValueError('A value error.')

        mock_file.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.post('/api/files/1/receive', headers=HEADERS, json={})
            self.assertEqual(response.json, {'message': 'A value error.'})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.files.shipment.validate_batch')
    @patch('ptmd.api.queries.files.shipment.save_samples')
    def test_receive_data_success(self, mock_save, mock_file, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class FileMock:
            def __init__(self):
                self.gdrive_id = '123'

            def shipment_was_received(self, at):
                pass

        mock_file.return_value = FileMock()
        mock_user().id = 1
        mock_user().role = 'admin'
        with app.test_client() as client:
            response = client.post('/api/files/1/receive', headers=HEADERS, json={})
            self.assertEqual(response.json, {'message': 'File 1 received successfully.'})
            self.assertEqual(response.status_code, 200)
            mock_save.assert_called_once_with("1")


class TestBatchValidator(TestCase):

    @patch('ptmd.api.queries.files.shipment.File')
    @patch('ptmd.api.queries.files.shipment.get_shipped_file', return_value=False)
    @patch('ptmd.api.queries.files.shipment.BatchUpdater')
    def test_success(self, mock_batch_updater, mock_shipped, mock_file):
        mock_batch_updater().file = 1
        mock_file.query.filter_by().first.return_value.organism.ptox_biosystem_name = 'test'
        self.assertEqual(validate_batch(1, "BB"), 1)
        self.assertEqual(validate_batch(1), mock_file.query.filter_by().first.return_value)

    @patch('ptmd.api.queries.files.shipment.File')
    def test_failed_404(self, mock_file):
        mock_file.query.filter_by().first.return_value = None
        with self.assertRaises(BatchError) as context:
            validate_batch(1, 'AA')
        self.assertEqual(context.exception.code, 404)
        self.assertEqual(context.exception.message, 'File 1 not found.')

    @patch('ptmd.api.queries.files.shipment.File')
    @patch('ptmd.api.queries.files.shipment.get_shipped_file', return_value=True)
    def test_failed_412(self, mock_shipped, mock_file):
        mock_file.query.filter_by().first.return_value.organism.ptox_biosystem_name = 'test'
        with self.assertRaises(BatchError) as context:
            validate_batch(1)
        self.assertEqual(context.exception.code, 412)
        self.assertEqual(context.exception.message, 'Batch already used with test')
