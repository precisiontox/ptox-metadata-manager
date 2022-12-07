from unittest import TestCase, skip
from unittest.mock import patch

from ptmd.clients import GoogleDriveConnector


class MockGoogleAuth:
    credentials = None
    access_token_expired = True

    def LoadCredentialsFile(self, credentials_file):
        pass

    def LocalWebserverAuth(self):
        pass

    def SaveCredentialsFile(self, credentials_file):
        pass

    def Refresh(self):
        pass

    def Authorize(self):
        pass


class MockGoogleDrive:

    def CreateFile(self, *args, **kwargs):
        class FileMock(dict):
            def Upload(self):
                return {'id': '1234'}
        return FileMock()


class TestGDriveUtils(TestCase):

    @patch('ptmd.clients.gdrive.core.GoogleAuth')
    def test_constructor(self, mock_google_auth):
        gdrive_connector = GoogleDriveConnector()
        self.assertIsNotNone(gdrive_connector.google_drive)
        gdrive_connector.connect()
        self.assertIsNotNone(gdrive_connector.google_drive)

        gdrive_connector.google_drive = None
        gdrive_connector._GoogleDriveConnector__google_auth = MockGoogleAuth()
        gdrive_connector.connect()
        self.assertIsNotNone(gdrive_connector.google_drive)

        gdrive_connector.google_drive = None
        gdrive_connector._GoogleDriveConnector__google_auth = MockGoogleAuth()
        gdrive_connector._GoogleDriveConnector__google_auth.credentials = True
        gdrive_connector._GoogleDriveConnector__google_auth.access_token_expired = False
        gdrive_connector.connect()
        self.assertIsNotNone(gdrive_connector.google_drive)

    @patch('ptmd.clients.gdrive.core.GoogleAuth')
    @patch('ptmd.clients.gdrive.core.directory_exist')
    def test_create_directories_skip(self, directory_exist, google_auth_mock):
        gdrive_connector = GoogleDriveConnector()
        gdrive_connector.create_directories()
        self.assertEqual(9, directory_exist.call_count)

    @patch('ptmd.clients.gdrive.core.GoogleAuth')
    @patch('ptmd.clients.gdrive.core.directory_exist', return_value=None)
    @patch('ptmd.clients.gdrive.core.GoogleDrive', return_value=MockGoogleDrive())
    def test_create_directories(self, directory_exist, google_auth_mock, create_file_mock):
        gdrive_connector = GoogleDriveConnector()
        folders_ids = gdrive_connector.create_directories()
        self.assertIsNone(folders_ids['root_directory'])
        for partner in folders_ids['partners']:
            self.assertIsNone(folders_ids['partners'][partner])


@skip("This is an integration test and should not be run as part of the unit tests")
class TestIntegrateGDrive(TestCase):

    def test_integrate(self):
        gdrive_connector = GoogleDriveConnector()
        folders_ids = gdrive_connector.create_directories()
        self.assertIsNotNone(folders_ids['root_directory'])
