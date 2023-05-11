from unittest import TestCase
from unittest.mock import patch

from ptmd.api import app


HEADERS = {'Content-Type': 'application/json'}


@patch('ptmd.api.queries.users.session')
@patch('ptmd.api.queries.utils.verify_jwt_in_request', return_value=None)
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
@patch('ptmd.api.queries.utils.get_current_user')
@patch('ptmd.api.queries.utils.check_role')
class TestCoreQueries(TestCase):

    @patch('ptmd.api.queries.core.Organism')
    def test_get_organisms(self, mock_organism, mock_role,
                           mock_get_current_user, mock_verify_jwt, mock_verify_in_request, mock_get_session):
        mock_organism.query.all().return_value = []
        mock_get_current_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/organisms', headers={'Authorization': f'Bearer {123}'})
            self.assertEqual(response.json['data'], [])
            self.assertEqual(response.status_code, 200)

    @patch('ptmd.api.queries.core.Organisation')
    def test_get_organisations(self, mock_organisation, mock_role,
                               mock_get_current_user, mock_verify_jwt, mock_verify_in_request, mock_get_session):
        mock_organisation.query.filter.all().return_value = []
        mock_get_current_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/organisations', headers={'Authorization': f'Bearer {123}'})
            self.assertEqual(response.json['data'], [])
            self.assertEqual(response.status_code, 200)

    @patch('ptmd.api.queries.core.Chemical')
    def test_get_chemicals(self, mock_chemical, mock_role,
                           mock_get_current_user, mock_verify_jwt, mock_verify_in_request, mock_get_session):
        mock_chemical.ptx_code = 1
        mock_chemical.query.filter.all().return_value = []
        mock_get_current_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/chemicals', headers={'Authorization': f'Bearer {123}'})
            self.assertEqual(response.json["data"], [])
            self.assertEqual(response.status_code, 200)
