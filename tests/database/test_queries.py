from unittest import TestCase
from unittest.mock import patch

from ptmd.database.queries import get_allowed_chemicals, get_allowed_organisms


class MockChemical:
    def __init__(self) -> None:
        self.common_name = 'A NAME'
        self.ptox_biosystem_name = 'ANOTHER NAME'


class MockQuery:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def all():
        return [MockChemical()]


class MockSession:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def query(*args, **kwargs):
        return MockQuery()

    def close(self):
        pass


class TestDBQueries(TestCase):

    @patch('ptmd.database.queries.get_session', return_value=MockSession())
    def test_get_allowed_chemicals(self, mock_get_session):
        self.assertEqual(get_allowed_chemicals(), ['A NAME'])

    @patch('ptmd.database.queries.get_session', return_value=MockSession())
    def test_get_allowed_organisms(self, mock_get_session):
        self.assertEqual(get_allowed_organisms(), ['ANOTHER NAME'])
