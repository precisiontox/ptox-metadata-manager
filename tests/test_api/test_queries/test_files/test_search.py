from unittest import TestCase
from unittest.mock import patch

from werkzeug.datastructures import ImmutableMultiDict

from ptmd.api import app
from ptmd.api.queries.files.search import get_state_input, get_integer_input


HEADERS = {'Content-Type': 'application/json'}


class TestSearchFiles(TestCase):

    def test_get_integer_input(self):
        arguments = ImmutableMultiDict([('replicates', 1), ('replicates_operator', 'gt')])
        expected = {'value': 1, 'operator': 'gt'}
        self.assertEqual(get_integer_input(arguments, 'replicates'), expected)

        arguments = ImmutableMultiDict([('replicates', 1)])
        expected = {'value': 1, 'operator': 'eq'}
        self.assertEqual(get_integer_input(arguments, 'replicates'), expected)
        arguments = ImmutableMultiDict([('replicates', 1), ('replicates_operator', 'invalid')])
        self.assertEqual(get_integer_input(arguments, 'replicates'), expected)

        arguments = ImmutableMultiDict([])
        self.assertEqual(get_integer_input(arguments, 'replicates'), None)

    def test_get_state_input(self):
        arguments = ImmutableMultiDict([('valid', 'true')])
        self.assertEqual(get_state_input(arguments), True)
        arguments = ImmutableMultiDict([('valid', 'True')])
        self.assertEqual(get_state_input(arguments), True)
        arguments = ImmutableMultiDict([('valid', '1')])
        self.assertEqual(get_state_input(arguments), True)
        arguments = ImmutableMultiDict([('valid', 1)])
        self.assertEqual(get_state_input(arguments), True)

        arguments = ImmutableMultiDict([('valid', 'false')])
        self.assertEqual(get_state_input(arguments), False)
        arguments = ImmutableMultiDict([('valid', 'False')])
        self.assertEqual(get_state_input(arguments), False)
        arguments = ImmutableMultiDict([('valid', '0')])
        self.assertEqual(get_state_input(arguments), False)
        arguments = ImmutableMultiDict([('valid', 0)])
        self.assertEqual(get_state_input(arguments), False)

        arguments = ImmutableMultiDict([])
        self.assertEqual(get_state_input(arguments), None)
        arguments = ImmutableMultiDict([('valid', 'invalid')])
        self.assertEqual(get_state_input(arguments), None)

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user')
    @patch('ptmd.api.queries.files.search.search_files', return_value={'data': []})
    def test_route_404(self, mock_search, mock_get_current_user, mock_verify_jwt_in_request, mock_jwt_required):
        mock_get_current_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/search', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {'message': 'No files found'})

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user')
    @patch('ptmd.api.queries.files.search.search_files', return_value={'data': ["file1", "file2"]})
    def test_route_200(self, mock_search, mock_get_current_user, mock_verify_jwt_in_request, mock_jwt_required):
        mock_get_current_user().role = 'admin'
        with app.test_client() as client:
            response = client.get('/api/files/search', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'data': ['file1', 'file2']})
