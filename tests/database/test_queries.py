from unittest import TestCase
from unittest.mock import patch

from ptmd.database.queries import (
    get_allowed_chemicals,
    get_allowed_organisms,
    get_organism_code,
    get_chemical_code_mapping
)


class MockChemical:
    def __init__(self) -> None:
        self.common_name = 'A NAME'
        self.ptox_biosystem_name = 'ANOTHER NAME'
        self.ptox_biosystem_code = 'A'
        self.ptx_code = 1

    def first(self) -> object:
        return self


class MockChemicalError(MockChemical):
    def first(self):
        return None


class MockQuery:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def all():
        return [MockChemical()]

    @staticmethod
    def filter_by(*args, **kwargs):
        return MockChemical()


class MockQueryError(MockQuery):
    @staticmethod
    def filter_by(*args, **kwargs):
        return MockChemicalError()


class MockSession:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def query(*args, **kwargs):
        return MockQuery()

    def close(self):
        pass


class MockSessionError(MockSession):
    @staticmethod
    def query(*args, **kwargs):
        return MockQueryError()


class TestDBQueries(TestCase):

    @patch('ptmd.database.queries.get_session', return_value=MockSession())
    def test_get_allowed_chemicals(self, mock_get_session):
        self.assertEqual(get_allowed_chemicals(), ['A NAME'])

    @patch('ptmd.database.queries.get_session', return_value=MockSession())
    def test_get_allowed_organisms(self, mock_get_session):
        self.assertEqual(get_allowed_organisms(), ['ANOTHER NAME'])

    @patch('ptmd.database.queries.get_session', return_value=MockSession())
    def test_get_organism_code(self, mock_get_session):
        self.assertEqual(get_organism_code('A'), 'A')

    @patch('ptmd.database.queries.get_session', return_value=MockSession())
    def test_get_chemical_code_mapping(self, mock_get_session):
        self.assertEqual(get_chemical_code_mapping(['A']), {'A NAME': '001'})

    @patch('ptmd.database.queries.get_session', return_value=MockSessionError())
    def test_database_errors_chemicals(self, mock_get_session):
        with self.assertRaises(ValueError) as context:
            get_chemical_code_mapping(['A'])
        self.assertEqual(str(context.exception), 'Chemical A not found in the database.')

    @patch('ptmd.database.queries.get_session', return_value=MockSessionError())
    def test_database_errors_organisms(self, mock_get_session):
        with self.assertRaises(ValueError) as context:
            get_organism_code('BBB')
        self.assertEqual(str(context.exception), 'Organism BBB not found in the database.')
