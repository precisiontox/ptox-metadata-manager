from unittest import TestCase
from unittest.mock import patch

from pydrive2.drive import GoogleDrive

from ptmd.lib.gdrive.utils import get_folder_id, get_file_information, find_files_in_folder


class TestGDriveUtils(TestCase):

    def test_directory_exist(self):
        mocked_value = {'id': 'ERREZR', 'title': 'test'}

        class MockGoogleDrive(GoogleDrive):

            def __init__(self, return_value=True):
                self.return_value = return_value

            def ListFile(self, *args, **kwargs):
                return self

            def GetList(self):
                return [mocked_value] if self.return_value else []

        self.assertEqual(get_folder_id(MockGoogleDrive(), 'test'), 'ERREZR')
        self.assertIsNotNone(get_folder_id(MockGoogleDrive(), 'test2', 'ERREZR'))
        self.assertIsNone(get_folder_id(MockGoogleDrive(return_value=False), 'test3'))

    @patch('ptmd.lib.gdrive.utils.GoogleDrive')
    def test_get_file_information(self, mocked_google_drive):
        folder_id = 'ERREZR'
        filename = 'test'
        query = f"title = '{filename}' and '{folder_id}' in parents and trashed=false"
        mocked_google_drive.ListFile().GetList.return_value = [{'id': folder_id, 'title': filename}]
        file_info = get_file_information(mocked_google_drive, folder_id, filename)
        self.assertEqual(file_info['id'], folder_id)
        mocked_google_drive.ListFile.assert_called_with({"q": query})

    @patch('ptmd.lib.gdrive.utils.GoogleDrive')
    def test_find_files_in_folder(self, mocked_google_drive):
        folder_id = 'ERREZR'
        query = f"'{folder_id}' in parents and trashed=false"
        mocked_google_drive.ListFile().GetList.return_value = [{'id': folder_id, 'title': 'test'}]
        files = find_files_in_folder(mocked_google_drive, folder_id)
        self.assertEqual(files[0]['id'], folder_id)
        mocked_google_drive.ListFile.assert_called_with({"q": query})
