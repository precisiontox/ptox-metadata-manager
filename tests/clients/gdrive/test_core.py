from os import path
from unittest import TestCase
from unittest.mock import patch

from pydrive2.auth import GoogleAuth

from ptmd.clients import GoogleDriveConnector


class MockGoogleAuth(GoogleAuth):
    credentials = None
    access_token_expired = True

    def LoadCredentialsFile(*args, **kwargs):
        pass

    def LocalWebserverAuth(*args, **kwargs):
        pass

    def SaveCredentialsFile(*args, **kwargs):
        pass

    def Refresh(*args, **kwargs):
        pass

    def Authorize(self, *args, **kwargs):
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

    def InsertPermission(self, *args, **kwargs):
        pass

    def GetContentFile(self, *args, **kwargs):
        return {"title": "title test"}


class MockGoogleDrive:
    def CreateFile(self, *args, **kwargs):
        return FileMock()


class MockGoogleDriveForFilename:
    def CreateFile(self, *args, **kwargs):
        return {"title": "title test"}


@patch('ptmd.clients.gdrive.core.GoogleAuth', return_value=MockGoogleAuth)
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
        self.assertEqual(11, content_exist_mock.call_count)

    @patch('ptmd.clients.gdrive.core.content_exist', return_value=None)
    def test_create_directories(self, google_drive_mock, content_exist_mock, google_auth_mock):
        gdrive_connector = GoogleDriveConnector()
        folders_ids = gdrive_connector.create_directories()
        self.assertIsNone(folders_ids['root_directory'])
        for partner in folders_ids['partners']:
            self.assertIsNone(folders_ids['partners'][partner]['g_drive'])
            self.assertIsNotNone(folders_ids['partners'][partner]['long_name'])

        gdrive_connector2 = GoogleDriveConnector()
        self.assertEqual(gdrive_connector, gdrive_connector2)
        gdrive_connector2.google_drive = None
        gdrive_connector2._GoogleDriveConnector__google_auth.access_token_expired = True
        gdrive_connector2.connect()
        self.assertIsNotNone(gdrive_connector2.google_drive)

    @patch('ptmd.clients.gdrive.core.content_exist', return_value={'id': '1234'})
    def test_upload_file(self, content_exist_mock, google_drive_mock, google_auth_mock):
        here = path.abspath(path.dirname(__file__))
        xlsx_file = path.join(here, '..', '..', 'data', 'excel', 'test.xlsx')
        gdrive_connector = GoogleDriveConnector()
        file_metadata = gdrive_connector.upload_file(file_path=xlsx_file,
                                                     directory_id=123)
        self.assertEqual(content_exist_mock.return_value, file_metadata)

    def test_download_file(self, google_drive_mock, google_auth_mock):
        gdrive_connector = GoogleDriveConnector()
        file_id = "123"
        file_metadata = gdrive_connector.download_file(file_id=file_id, filename='test.xlsx')
        self.assertIn('test.xlsx', file_metadata)


@patch('ptmd.clients.gdrive.core.GoogleAuth', return_value=MockGoogleAuth)
@patch('ptmd.clients.gdrive.core.GoogleDrive', return_value=MockGoogleDriveForFilename())
class TestGetFileName(TestCase):
    def test_get_filename(self, google_drive_mock, google_auth_mock):
        gdrive_connector = GoogleDriveConnector()
        filename = gdrive_connector.get_filename(file_id="123")
        self.assertEqual(filename, "title test")
