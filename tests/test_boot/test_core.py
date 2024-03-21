from unittest import TestCase
from unittest.mock import patch

from ptmd.boot import initialize
from ptmd.boot.core import create_download_directory
from ptmd.const import DOWNLOAD_DIRECTORY_PATH


class MockUser:
    def __init__(self):
        self.username = 'user1'
        self.id = "123"
        self.name = 'UOX'
        self.gdrive_id = '1234'


@patch('ptmd.boot.core.Base')
@patch('ptmd.boot.core.User')
@patch('ptmd.boot.core.GoogleDriveConnector')
@patch('ptmd.boot.core.seed_db', return_value=({}, {}, {}, {}))
class TestInitializeApp(TestCase):

    def test_init_no_user(self, mock_boot, mock_gdc, mock_user, mock_base):
        mock_user.query.first.return_value = None
        mock_gdc.return_value.create_directories.return_value = ({'partners': []}, {})
        initialize()
        mock_boot.assert_called_once()
        mock_base.metadata.create_all.assert_called_once()
        mock_gdc.assert_called_once()

    def test_init_with_users(self, mock_boot, mock_gdc, mock_user, mock_base):
        mock_user.query.first.return_value = MockUser()
        initialize()
        mock_boot.assert_not_called()
        mock_base.metadata.create_all.assert_called_once()
        mock_gdc.assert_called_once()

    def test_init_error(self, mock_boot, mock_gdc, mock_user, mock_base):
        mock_user.query.first.side_effect = Exception('Error')
        with self.assertRaises(Exception):
            initialize()
        mock_boot.assert_not_called()
        mock_base.metadata.drop_all.assert_called_once()
        mock_gdc.assert_called_once()


class TestUtils(TestCase):

    @patch('ptmd.boot.core.mkdir')
    @patch('ptmd.boot.core.exists', return_value=False)
    def test_create_download_directory_true(self, exists_mock, mkdir_mock):
        create_download_directory()
        exists_mock.assert_called_once_with(DOWNLOAD_DIRECTORY_PATH)
        mkdir_mock.assert_called_once_with(DOWNLOAD_DIRECTORY_PATH)

    @patch('ptmd.boot.core.mkdir')
    @patch('ptmd.boot.core.exists', return_value=True)
    def test_create_download_directory_false(self, exists_mock, mkdir_mock):
        create_download_directory()
        exists_mock.assert_called_once_with(DOWNLOAD_DIRECTORY_PATH)
        mkdir_mock.assert_not_called()
