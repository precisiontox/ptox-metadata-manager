from unittest import TestCase
from unittest.mock import patch

from ptmd.database import get_allowed_organisms, get_organism_code, create_organisms


class MockModel:
    def __init__(self, *args, **kwargs):
        self.ptox_biosystem_name = 'ANOTHER NAME'
        self.ptox_biosystem_code = 'A'


class TestOrganismsQueries(TestCase):
    @patch('ptmd.database.queries.organisms.Organism')
    def test_get_allowed_organisms(self, mock_organism):
        mock_organism.query.all.return_value = [MockModel()]
        self.assertEqual(get_allowed_organisms(), ['ANOTHER NAME'])

    @patch('ptmd.database.queries.organisms.Organism')
    def test_get_organism_code(self, mock_organism):
        mock_organism.query.filter().first.return_value = MockModel()
        self.assertEqual(get_organism_code('A'), 'A')

        mock_organism.query.filter().first.return_value = None
        with self.assertRaises(ValueError) as context:
            get_organism_code('BBB')
        self.assertEqual(str(context.exception), 'Organism BBB not found in the database.')

    def test_create_organisms(self):
        with patch('ptmd.database.queries.organisms.session'):
            organisms_input = [{"scientific_name": "test", "ptox_biosystem_name": "A", "ptox_biosystem_code": "A"}]
            organisms = create_organisms(organisms=organisms_input)
            organism = dict(organisms['A'])
            exp = {'organism_id': None, 'scientific_name': 'test', 'ptox_biosystem_name': 'A', "ptox_biosystem_code": "A"}
            self.assertEqual(organism, exp)
            organisms = create_organisms(organisms=[{"test": 1}])
            self.assertEqual(organisms, {})
