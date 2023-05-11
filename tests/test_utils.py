from os import path
from unittest import TestCase
from unittest.mock import patch, mock_open

from ptmd.utils import init, initialize, create_config_file


class MockedQuery:
    @staticmethod
    def all():
        return []


class MockGoogleDriveConnector:

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def create_directories(*args, **kwargs):
        return {'partners': ['partner1', 'partner2']}


class MockUser:
    def __init__(self):
        self.username = 'user1'
        self.id = "123"
        self.name = 'UOX'
        self.gdrive_id = '1234'


@patch('ptmd.utils.Base')
@patch('ptmd.utils.User')
@patch('ptmd.utils.GoogleDriveConnector', return_value=MockGoogleDriveConnector)
@patch('ptmd.utils.boot', return_value=({}, {}, {}, {}))
class TestUtils(TestCase):

    def test_init_no_user(self, mock_boot, mock_gdc, mock_user, mock_base):
        mock_user.query.all.return_value = None
        self.assertEqual(initialize(users=[]), ({}, {}))

    @patch('ptmd.utils.Organisation')
    def test_init_with_users(self, mock_org, mock_boot, mock_gdc, mock_user, mock_base):
        mock_org.query.all.return_value = []
        mock_user.query.all.return_value = [MockUser()]
        self.assertEqual(initialize(users=[]), ({'user1': '123'}, {}))


class TestAPIUtilities(TestCase):

    @patch('ptmd.utils.initialize')
    @patch('ptmd.utils.create_config_file', return_value={})
    def test_init(self, create_config_file_dump, mock_init):
        expected = [{
            'username': 'admin',
            'password': 'admin',
            'organisation_id': 1,
            'role': 'admin',
            'email': 'domwow13@gmail.com'
        }]
        init()
        mock_init.assert_called_once()
        mock_init.assert_called_with(users=expected)


@patch('ptmd.utils.exists', return_value=False)
@patch('ptmd.utils.dump', return_value=True)
class TestCreateConfigFile(TestCase):

    def setUp(self):
        self.mock_path = path.join(path.dirname(path.abspath(__file__)), 'data', 'test_config.yaml')
        self.mock_settings = patch('ptmd.utils.SETTINGS_FILE_PATH', self.mock_path)

    def test_create_config_file(self, mock_dump, mock_exists):
        with self.mock_settings:
            with patch("builtins.open", mock_open(read_data="data")):
                gdrive_settings = create_config_file()
                mock_exists.assert_called_once()
                mock_dump.assert_called_once()
                self.assertIsNotNone(gdrive_settings)
