from unittest import TestCase
from unittest.mock import patch

from ptmd.api import app


HEADERS = {'Content-Type': 'application/json'}


@patch('ptmd.api.queries.users.session')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
class TestCoreQueries(TestCase):

    @patch('ptmd.api.queries.core.Organism')
    def test_get_organisms(self, mock_organism, mock_get_session, mock_jwt_required):
        mock_organism.query.all().return_value = []
        with app.test_client() as client:
            response = client.get('/api/organisms', headers={'Authorization': f'Bearer {123}'})
            self.assertEqual(response.json['data'], [])
            self.assertEqual(response.status_code, 200)

    @patch('ptmd.api.queries.core.Organisation')
    def test_get_organisations(self, mock_organisation, mock_get_session, mock_jwt_required):
        mock_organisation.query.filter.all().return_value = []
        with app.test_client() as client:
            response = client.get('/api/organisations', headers={'Authorization': f'Bearer {123}'})
            self.assertEqual(response.json['data'], [])
            self.assertEqual(response.status_code, 200)

    @patch('ptmd.api.queries.core.Chemical')
    def test_get_chemicals(self, mock_chemical, mock_get_session, mock_jwt_required):
        mock_chemical.ptx_code = 1
        mock_chemical.query.filter.all().return_value = []
        with app.test_client() as client:
            response = client.get('/api/chemicals', headers={'Authorization': f'Bearer {123}'})
            self.assertEqual(response.json["data"], [])
            self.assertEqual(response.status_code, 200)
