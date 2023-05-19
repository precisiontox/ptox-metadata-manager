from unittest import TestCase
from unittest.mock import patch

from ptmd.database.queries import (
    get_allowed_chemicals,
    create_chemicals,
    get_chemical_code_mapping,
    get_chemicals_from_name
)


class MockModel:
    def __init__(self, *args, **kwargs):
        self.common_name = 'A NAME'
        self.ptx_code = 1


class TestChemicalQueries(TestCase):

    @patch('ptmd.database.models.chemical.get_current_user')
    def test_create_chemicals(self, mock_current_user):
        mock_current_user.return_value.role = 'admin'
        with patch('ptmd.database.queries.chemicals.session'):
            chemical_input = [{"common_name": "test", "formula": "test", "cas": "test", "ptx_code": 1}]
            expected_chemical = {
                'chemical_id': None, 'common_name': 'test', 'cas': 'test', 'formula': 'test', 'ptx_code': "PTX001"
            }
            chemicals = create_chemicals(chemicals=chemical_input)
            self.assertEqual(dict(chemicals['test']), expected_chemical)
            chemicals = create_chemicals(chemicals=[{"test": 1}])
            self.assertEqual(chemicals, {})

    @patch('ptmd.database.queries.chemicals.Chemical')
    def test_get_allowed_chemicals(self, mock_chemical):
        mock_chemical.query.all.return_value = [MockModel()]
        self.assertEqual(get_allowed_chemicals(), ['A NAME'])

    @patch('ptmd.database.queries.chemicals.Chemical')
    def test_get_chemical_code_mapping(self, mock_chemical):
        mock_chemical.query.filter().first.return_value = MockModel()
        self.assertEqual(get_chemical_code_mapping(['A']), {'A NAME': '001'})

        mock_chemical.query.filter().first.return_value = None
        with self.assertRaises(ValueError) as context:
            get_chemical_code_mapping(['A'])
        self.assertEqual(str(context.exception), 'Chemical A not found in the database.')

    @patch('ptmd.database.queries.chemicals.Chemical')
    def test_get_chemicals_from_name(self, mock_chemical):
        mock_chemical.query.filter().all.return_value = ['A NAME']
        self.assertEqual(get_chemicals_from_name(["A"]), ['A NAME'])
