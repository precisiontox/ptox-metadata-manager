from unittest import TestCase

from pydrive2.drive import GoogleDrive

from ptmd.lib.gdrive.utils import content_exist


class TestGDriveUtils(TestCase):

    def test_directory_exist(self):
        mocked_value = {'id': 'ERREZR', 'title': 'test'}

        class MockGoogleDrive(GoogleDrive):

            def __init__(self, return_value=True):
                self.return_value = return_value

            def ListFile(self, query):
                return self

            def GetList(self):
                return [mocked_value] if self.return_value else []

        self.assertEqual(content_exist(MockGoogleDrive(), 'test'), mocked_value)
        self.assertIsNotNone(content_exist(MockGoogleDrive(), 'test2', 'ERREZR'))
        self.assertIsNone(content_exist(MockGoogleDrive(return_value=False), 'test3'))
        self.assertIsNone(content_exist(
            google_drive=MockGoogleDrive(return_value=False),
            folder_name='test3',
            type_='file',
            parent="ERREZR"
        ))
