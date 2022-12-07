from unittest import TestCase

from pydrive2.drive import GoogleDrive

from ptmd.clients.gdrive.utils import directory_exist


class TestGDriveUtils(TestCase):

    def test_directory_exist(self):
        class MockGoogleDrive(GoogleDrive):

            def __init__(self, return_value=True):
                self.return_value = return_value

            def ListFile(self, query):
                return self

            def GetList(self):
                return [{'id': 'ERREZR', 'title': 'test'}] if self.return_value else []

        self.assertEqual(directory_exist(MockGoogleDrive(), 'test'), 'ERREZR')
        self.assertIsNotNone(directory_exist(MockGoogleDrive(), 'test2', 'ERREZR'))
        self.assertIsNone(directory_exist(MockGoogleDrive(return_value=False), 'test3'))
