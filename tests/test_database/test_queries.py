from unittest import TestCase
from unittest.mock import patch

from ptmd.database.queries import (
    get_allowed_chemicals,
    get_allowed_organisms,
    get_organism_code,
    get_chemical_code_mapping
)


class MockModel:
    def __init__(self) -> None:
        self.common_name = 'A NAME'
        self.ptox_biosystem_name = 'ANOTHER NAME'
        self.ptox_biosystem_code = 'A'
        self.ptx_code = 1

    def first(self) -> object:
        return self


class MockModelError(MockModel):
    def first(self):
        return None


class MockQuery:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def all():
        return [MockModel()]

    @staticmethod
    def filter_by(*args, **kwargs):
        return MockModel()

    @staticmethod
    def filter(*args, **kwargs):
        return MockModel()


class MockQueryError(MockQuery):
    @staticmethod
    def filter_by(*args, **kwargs):
        return MockModelError()

    @staticmethod
    def filter(*args, **kwargs):
        return MockModelError()


class TestDBQueries(TestCase):

    @patch('ptmd.database.queries.Chemical')
    def test_get_allowed_chemicals(self, mock_chemical):
        mock_chemical.query = MockQuery()
        self.assertEqual(get_allowed_chemicals(), ['A NAME'])

    @patch('ptmd.database.queries.Organism')
    def test_get_allowed_organisms(self, mock_organism):
        mock_organism.query = MockQuery()
        self.assertEqual(get_allowed_organisms(), ['ANOTHER NAME'])

    @patch('ptmd.database.queries.Organism')
    def test_get_organism_code(self, mock_organism):
        mock_organism.query = MockQuery()
        self.assertEqual(get_organism_code('A'), 'A')

    @patch('ptmd.database.queries.Chemical')
    def test_get_chemical_code_mapping(self, mock_chemical):
        mock_chemical.query = MockQuery()
        self.assertEqual(get_chemical_code_mapping(['A']), {'A NAME': '001'})

    @patch('ptmd.database.queries.Chemical')
    def test_database_errors_chemicals(self, mock_chemical):
        mock_chemical.query = MockQueryError()
        with self.assertRaises(ValueError) as context:
            get_chemical_code_mapping(['A'])
        self.assertEqual(str(context.exception), 'Chemical A not found in the database.')

    @patch('ptmd.database.queries.Organism')
    def test_database_errors_organisms(self, mock_organism):
        mock_organism.query = MockQueryError()
        with self.assertRaises(ValueError) as context:
            get_organism_code('BBB')
        self.assertEqual(str(context.exception), 'Organism BBB not found in the database.')
