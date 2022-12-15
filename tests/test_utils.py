from unittest import TestCase
from unittest.mock import patch

from ptmd.utils import initialize


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
@patch('ptmd.utils.pull_chemicals_from_ptox_db', return_value=[])
@patch('ptmd.utils.pull_organisms_from_ptox_db', return_value=[])
class TestUtils(TestCase):

    def test_init_no_user(self, mock_chemicals, mock_organisms, mock_boot, mock_gdc):
        mocked_session = MockedSession()
        self.assertEqual(initialize(users=[], session=mocked_session), ({}, {}))

    def test_init_with_users(self, mock_chemicals, mock_organisms, mock_boot, mock_gdc):
        def return_users(*args, **kwargs):
            return [MockUser()]

        def return_query(*args, **kwargs):
            return MockedQuery()

        setattr(MockedQuery, 'all', return_users)
        setattr(MockedSession, 'query', return_query)
        mocked_session = MockedSession()
        self.assertEqual(initialize(users=[], session=mocked_session), ({'user1': '123'}, {'UOX': '1234'}))
