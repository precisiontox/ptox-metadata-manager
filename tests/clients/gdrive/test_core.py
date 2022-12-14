from os import path
from unittest import TestCase
from unittest.mock import patch

from pydrive2.auth import GoogleAuth

from ptmd.clients import GoogleDriveConnector


class MockGoogleAuth(GoogleAuth):
    credentials = None
    access_token_expired = True

    def LoadCredentialsFile(self, *args, **kwargs):
        pass

    def LocalWebserverAuth(self, *args, **kwargs):
        pass

    def SaveCredentialsFile(self, *args, **kwargs):
        pass

    def Refresh(self):
        pass

    def Authorize(self):
        pass

    def SaveCredentials(self, backend=None):
        pass


class ContentMock:
    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        pass


class FileMock(dict):
    content = ContentMock()

    def Upload(self):
        return {'id': '1234'}

    def SetContentFile(self, *args, **kwargs):
        pass


class MockGoogleDrive:
    def CreateFile(self, *args, **kwargs):
        return FileMock()


@patch('ptmd.clients.gdrive.core.GoogleAuth')
@patch('ptmd.clients.gdrive.core.GoogleDrive', return_value=MockGoogleDrive())
class TestGDriveConnector(TestCase):

    def test_constructor(self, google_drive_mock, google_auth_mock):
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

    @patch('ptmd.clients.gdrive.core.content_exist', return_value=None)
    def test_create_directories_skip(self, content_exist_mock, google_drive_mock, google_auth_mock):
        gdrive_connector = GoogleDriveConnector()
        gdrive_connector.create_directories()
        self.assertEqual(10, content_exist_mock.call_count)

    @patch('ptmd.clients.gdrive.core.content_exist', return_value=None)
    def test_create_directories(self, google_drive_mock, content_exist_mock, google_auth_mock):
        gdrive_connector = GoogleDriveConnector()
        folders_ids = gdrive_connector.create_directories()
        self.assertIsNone(folders_ids['root_directory'])
        for partner in folders_ids['partners']:
            self.assertIsNone(folders_ids['partners'][partner])

        gdrive_connector2 = GoogleDriveConnector()
        self.assertEqual(gdrive_connector, gdrive_connector2)
        gdrive_connector2._GoogleDriveConnector__google_auth.access_token_expired = True
        self.assertIsNotNone(gdrive_connector2.google_drive)

    @patch('ptmd.clients.gdrive.core.content_exist', return_value={'id': '1234'})
    def test_upload_file(self, content_exist_mock, google_drive_mock, google_auth_mock):
        here = path.abspath(path.dirname(__file__))
        xlsx_file = path.join(here, '..', '..', 'data', 'excel', 'test.xlsx')
        gdrive_connector = GoogleDriveConnector()
        file_metadata = gdrive_connector.upload_file(file_path=xlsx_file,
                                                     directory_id=123)
        self.assertEqual(content_exist_mock.return_value, file_metadata)
