from os import path, remove
from unittest import TestCase
from unittest.mock import patch

from sqlalchemy.orm import Session

from ptmd.const import CONFIG
from ptmd.utils import get_session, init


from ptmd.utils import initialize, create_config_file


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


class MockedSession:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def query(*args, **kwargs):
        return MockedQuery()


class MockUser:
    def __init__(self):
        self.username = 'user1'
        self.id = "123"
        self.name = 'UOX'
        self.gdrive_id = '1234'


@patch('ptmd.utils.GoogleDriveConnector', return_value=MockGoogleDriveConnector)
@patch('ptmd.utils.boot', return_value=({}, {}, {}, {}))
class TestUtils(TestCase):

    def test_init_no_user(self, mock_boot, mock_gdc):
        mocked_session = MockedSession()
        self.assertEqual(initialize(users=[], session=mocked_session), ({}, {}))

    def test_init_with_users(self, mock_boot, mock_gdc):
        def return_users(*args, **kwargs):
            return [MockUser()]

        def return_query(*args, **kwargs):
            return MockedQuery()

        setattr(MockedQuery, 'all', return_users)
        setattr(MockedSession, 'query', return_query)
        mocked_session = MockedSession()
        self.assertEqual(initialize(users=[], session=mocked_session), ({'user1': '123'}, {'UOX': '1234'}))


class TestAPIUtilities(TestCase):

    @patch('ptmd.utils.initialize')
    @patch('ptmd.utils.get_session', return_value=Session())
    @patch('ptmd.utils.create_config_file', return_value={})
    def test_init(self, create_config_file_dump, mock_get_session, mock_init):
        init()
        mock_init.assert_called_once()
        mock_init.assert_called_with(users=[{'username': 'admin', 'password': 'admin', 'organisation': 'UOX'}],
                                     session=mock_get_session.return_value)

    @patch('ptmd.database.Base.metadata.create_all', return_value=None)
    @patch('ptmd.database.utils.create_engine', return_value="abc")
    def test_get_session(self, mock_create_engine, mock_create_all):
        session = get_session()
        self.assertIsInstance(session, Session)
        mock_create_engine.assert_called_once()
        mock_create_engine.assert_called_with(CONFIG['SQLALCHEMY_DATABASE_URL'])


@patch('ptmd.utils.exists', return_value=False)
@patch('ptmd.utils.dump', return_value=True)
class TestCreateConfigFile(TestCase):

    def setUp(self):
        self.mock_path = path.join(path.dirname(path.abspath(__file__)), 'data', 'test_config.yaml')
        self.mock_settings = patch('ptmd.utils.SETTINGS_FILE_PATH', self.mock_path)

    def test_create_config_file(self, mock_dump, mock_exists):
        with self.mock_settings:
            gdrive_settings = create_config_file()
            mock_exists.assert_called_once()
            mock_dump.assert_called_once()
            self.assertIsNotNone(gdrive_settings)
            remove(self.mock_path)
