from unittest import TestCase
from unittest.mock import patch

from ptmd.clients import pull_organisms_from_ptox_db, pull_chemicals_from_ptox_db
from ptmd.const import CONFIG


class MockedResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self.json_data = json_data

    def json(self):
        return self.json_data


CHEMICALS = {"chemical": [
    {'ptx_code': 100, 'name_hash_id': '-'},
    {'ptx_code': 996, 'name_hash_id': 'hello'}
]}
ORGANISMS = {"organism": []}
MOCKED_CHEMICAL_RESPONSE = MockedResponse(200, CHEMICALS)
MOCKED_ORGANISM_RESPONSE = MockedResponse(200, ORGANISMS)
MOCKED_ERROR = MockedResponse(400, {'errors': 'error'})
DB_URL = CONFIG['PTOX_API_ENDPOINT']


class TestQueries(TestCase):

    def test_pull_chemicals_from_ptox_db_success(self):
        with patch('ptmd.clients.pretox.queries.post', return_value=MOCKED_CHEMICAL_RESPONSE):
            chemicals = pull_chemicals_from_ptox_db()
            self.assertEqual(chemicals,
                             [{'ptx_code': 100, 'name_hash_id': None}, {'ptx_code': 996, 'name_hash_id': 'hello'}])

    def test_pull_chemicals_from_ptox_db_error(self):
        with patch('ptmd.clients.pretox.queries.post', return_value=MOCKED_ERROR):
            with self.assertRaises(ConnectionError) as context:
                pull_chemicals_from_ptox_db()
            error: str = 'Error fetching chemicals from the precision toxicology API at %s: error' % DB_URL
            self.assertTrue(error in str(context.exception))

    def test_pull_organisms_from_ptox_db_success(self):
        with patch('ptmd.clients.pretox.queries.post', return_value=MOCKED_ORGANISM_RESPONSE):
            organisms = pull_organisms_from_ptox_db()
            self.assertEqual(organisms, [])

    def test_pull_organisms_from_ptox_db_error(self):
        with patch('ptmd.clients.pretox.queries.post', return_value=MOCKED_ERROR):
            with self.assertRaises(ConnectionError) as context:
                pull_organisms_from_ptox_db()
            error: str = 'Error fetching organisms from the precision toxicology API at %s: error' % DB_URL
            self.assertTrue(error in str(context.exception))
