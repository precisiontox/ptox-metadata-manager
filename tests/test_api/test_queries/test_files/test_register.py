from unittest import TestCase
from unittest.mock import patch

from json import dumps as json_dumps

from ptmd.api import app


class MockGoogleDrive:
    def __init__(self, *args, **kwargs):
        pass

    def get_filename(self, *args, **kwargs):
        return 'filename'

    def download_file(self, *args, **kwargs):
        return 'filepath'

    def upload_file(self, *args, **kwargs):
        return {'id': 123}


class MockGoogleDriveError(MockGoogleDrive):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def upload_file(self, *args, **kwargs):
        return None


HEADERS = {'Content-Type': 'application/json'}


class TestRegisterFile(TestCase):

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.routes.register_gdrive_file', return_value=({'message': 'File added successfully.'}, 200))
    def test_route(self, mock_validate, mock_jwt):
        with app.test_client() as test_client:
            response = test_client.post('api/files/register')
        self.assertEqual(response.json, {'message': 'File added successfully.'})

    @patch('ptmd.api.queries.files.register.session')
    @patch('ptmd.api.queries.users.session')
    @patch('ptmd.api.queries.files.register.GoogleDriveConnector', return_value=MockGoogleDrive())
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.queries.files.create.get_current_user')
    @patch('ptmd.api.queries.files.register.get_current_user')
    @patch('ptmd.api.queries.files.register.File')
    @patch('ptmd.api.queries.utils.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user')
    def test_register_file_validation_error(self, mock_user,
                                            mock_jwt, mock_file, mock_jwt_1, mock_jwt_2, mock_verify_jwt,
                                            mock_gdrive, mock_session_1, mock_session_2):
        mock_jwt_1.id = 123
        mock_jwt_2.id = 123
        mock_user().role = 'admin'
        with app.test_client() as test_client:
            external_file = {'test': "test"}
            file = test_client.post('/api/files/register', headers={'Authorization': f'Bearer {123}', **HEADERS},
                                    data=json_dumps(external_file))
            self.assertEqual(file.json, {'message': "Field file_id is required."})
            self.assertEqual(file.status_code, 400)

    @patch('ptmd.api.queries.files.register.session')
    @patch('ptmd.api.queries.files.register.GoogleDriveConnector', return_value=MockGoogleDrive())
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.queries.files.register.File')
    @patch('ptmd.api.queries.utils.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user')
    @patch('ptmd.api.queries.files.register.Organisation')
    @patch('ptmd.api.queries.files.register.get_current_user')
    @patch('ptmd.api.queries.files.register.extract_data_from_spreadsheet')
    @patch('ptmd.api.queries.files.register.remove')
    def test_register_file_validation_success(self, mock_rm, mock_data, mock_user, mock_organisation,
                                              mock_get_user, mock_jwt_in_request, mock_file,
                                              mock_verify_jwt, mock_gdrive, mock_session):
        mock_get_user().role = 'admin'
        mock_file.return_value.file_id = '123'

        mock_organisation.query.filter().first.return_value.gdrive_id = '123'
        mock_organisation.query.filter().first.return_value.name = 'test'
        mock_user().id = 1

        with app.test_client() as client:
            with patch('ptmd.api.queries.files.register.jsonify') as mock_jsonify:
                external_file = {'file_id': '123', 'batch': 'AA', 'organism': 'human', 'partner': 'partner'}
                client.post('/api/files/register',
                            headers={'Authorization': f'Bearer {123}', **HEADERS},
                            data=json_dumps(external_file))
                mock_rm.assert_called_once_with('filepath')
                mock_data.assert_called_once_with('filepath')
                mock_session.add.assert_called_once()
                mock_session.commit.assert_called_once()
                mock_jsonify.assert_called_once_with(
                    {'message': 'file 123 was successfully created with internal id 123', 'file': {}}
                )

    @patch('ptmd.api.queries.files.register.session')
    @patch('ptmd.api.queries.files.register.GoogleDriveConnector', return_value=MockGoogleDriveError())
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.queries.files.register.File')
    @patch('ptmd.api.queries.utils.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user')
    @patch('ptmd.api.queries.files.register.Organisation')
    @patch('ptmd.api.queries.files.register.get_current_user')
    @patch('ptmd.api.queries.files.register.extract_data_from_spreadsheet')
    @patch('ptmd.api.queries.files.register.remove')
    def test_register_file_error_upload(self, mock_rm, mock_data, mock_user, mock_organisation,
                                        mock_get_user, mock_jwt_in_request, mock_file,
                                        mock_verify_jwt, mock_gdrive, mock_session):
        mock_get_user().role = 'admin'
        mock_file.return_value.file_id = '123'

        mock_organisation.query.filter().first.return_value.gdrive_id = '123'
        mock_organisation.query.filter().first.return_value.name = 'test'
        mock_user().id = 1

        with app.test_client() as client:
            with patch('ptmd.api.queries.files.register.jsonify') as mock_jsonify:
                external_file = {'file_id': '123', 'batch': 'AA', 'organism': 'human', 'partner': 'partner'}
                response = client.post('/api/files/register',
                                       headers={'Authorization': f'Bearer {123}', **HEADERS},
                                       data=json_dumps(external_file))
                mock_jsonify.assert_called_once_with({'message': "File '123' could not be uploaded."})
                self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.files.register.get_current_user')
    @patch('ptmd.api.queries.utils.verify_jwt_in_request')
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user')
    @patch('ptmd.api.queries.files.register.GoogleDriveConnector')
    def test_register_file_database_errors(self, mock_gdrive, mock_get_user,
                                           mock_jwt_in_request, mock_verify_jwt, mock_get_current_user):
        mock_get_user().role = 'admin'
        mock_get_current_user().id = 1
        mock_gdrive.return_value.get_filename.return_value = None
        with app.test_client() as test_client:
            response = test_client.post('api/files/register', data=json_dumps({
                'file_id': '123',
                'batch': 'AA',
                'organism': 'human',
                'partner': 'UOB'
            }), headers=HEADERS)
            self.assertEqual(response.json, {'message': "File '123' does not exist."})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.files.register.get_current_user')
    @patch('ptmd.api.queries.utils.verify_jwt_in_request')
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user')
    @patch('ptmd.api.queries.files.register.GoogleDriveConnector')
    @patch('ptmd.api.queries.files.register.remove')
    @patch('ptmd.api.queries.files.register.extract_data_from_spreadsheet', return_value=None)
    def test_register_file_wrong_data(self, mock_data, mock_rm, mock_gdrive, mock_get_user,
                                      mock_jwt_in_request, mock_verify_jwt, mock_get_current_user):
        mock_get_user().role = 'admin'
        mock_get_current_user().id = 1
        mock_gdrive.return_value.download_file.return_value = None
        with app.test_client() as test_client:
            response = test_client.post('api/files/register', data=json_dumps({
                'file_id': '123',
                'batch': 'AA',
                'organism': 'human',
                'partner': 'UOB'
            }), headers=HEADERS)
            self.assertEqual(response.json, {'message': "File '123' does not contain the required data."})
            self.assertEqual(response.status_code, 400)
