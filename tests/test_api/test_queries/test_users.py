from unittest import TestCase
from unittest.mock import patch
from json import dumps
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from ptmd.api import app

HEADERS = {'Content-Type': 'application/json'}


@patch('ptmd.api.queries.utils.verify_jwt_in_request', return_value=None)
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
@patch('ptmd.api.queries.utils.get_current_user')
class TestUserQueries(TestCase):

    def test_login(self, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        mock_get_current_user().role = 'admin'
        with app.test_client() as client:
            response = client.post('/api/session',
                                   headers={'Authorization': f'Bearer {123}', **HEADERS},
                                   data=dumps({}))
            self.assertEqual(response.json, {'msg': 'Missing username or password'})
            self.assertEqual(response.status_code, 400)

            with patch('ptmd.api.queries.users.login_user', return_value=("hi", 200)) as mocked:
                client.post('/api/session',
                            headers={'Authorization': f'Bearer {123}', **HEADERS},
                            data=dumps({"username": "test", "password": "test"}))
                mocked.assert_called_with(username='test', password='test')

    @patch('ptmd.api.queries.users.session')
    @patch('ptmd.api.queries.users.User')
    def test_create_user(self, mock_user,
                         mock_session, mock_get_current_user,
                         mock_verify_jwt, mock_verify_in_request):
        mock_get_current_user().role = 'admin'
        mock_user.return_value = {'id': None, 'username': '1234', 'organisation': None, 'files': []}
        user_data = {
            "username": "1234",
            "password": "1234",
            "confirm_password": "1234",
            "organisation_id": None,
            "email": "t@t.com"
        }
        with app.test_client() as client:
            created_user = client.post('/api/users',
                                       headers={'Authorization': f'Bearer {123}', **HEADERS},
                                       data=dumps(user_data))
            self.assertEqual(created_user.json,
                             {'msg': {'error': "None is not of type 'number'", 'field': 'organisation_id'}})

            user_data['organisation_id'] = "abc"
            created_user = client.post('/api/users',
                                       headers={'Authorization': f'Bearer {123}', **HEADERS},
                                       data=dumps(user_data))
            self.assertEqual(created_user.json,
                             {'msg': {'error': "'abc' is not of type 'number'", 'field': 'organisation_id'}})

            user_data['confirm_password'] = '124'
            user_data['organisation_id'] = 1
            created_user = client.post('/api/users',
                                       headers={'Authorization': f'Bearer {123}', **HEADERS},
                                       data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': "Passwords do not match"})

            user_data['confirm_password'] = '1234'
            created_user = client.post('/api/users',
                                       headers={'Authorization': f'Bearer {123}', **HEADERS},
                                       data=dumps(user_data))
            self.assertEqual(created_user.json, {'files': [], 'id': None, 'organisation': None, 'username': '1234'})

            mock_session.add.side_effect = IntegrityError(None, None, None)
            created_user = client.post('/api/users',
                                       headers={'Authorization': f'Bearer {123}', **HEADERS},
                                       data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': 'Username already taken'})

    @patch('ptmd.api.queries.users.session')
    @patch('ptmd.api.queries.users.get_jwt', return_value={'sub': 1})
    @patch('ptmd.api.queries.users.User')
    def test_change_pwd(self, mock_user, mock_jwt, mock_session,
                        mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        user_data = {"old_password": "1234", "new_password": "1234"}
        mock_get_current_user().role = 'admin'
        with app.test_client() as client:
            created_user = client.put('/api/users',
                                      headers={'Authorization': f'Bearer {123}', **HEADERS},
                                      data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': 'Missing new_password or confirm_password'})

            user_data['confirm_password'] = '456'
            created_user = client.put('/api/users',
                                      headers={'Authorization': f'Bearer {123}', **HEADERS},
                                      data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': 'Passwords do not match'})

            user_data['confirm_password'] = '1234'
            mock_user.query.filter().first().change_password.return_value = False
            created_user = client.put('/api/users',
                                      headers={'Authorization': f'Bearer {123}', **HEADERS},
                                      data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': 'Wrong password'})

            mock_user.query.filter().first().change_password.return_value = True
            created_user = client.put('/api/users',
                                      headers={'Authorization': f'Bearer {123}', **HEADERS},
                                      data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': 'Password changed successfully'})

            mock_get_current_user().role = 'banned'
            created_user = client.put('/api/users',
                                      headers={'Authorization': f'Bearer {123}', **HEADERS},
                                      data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': 'You are not authorized to access this route'})

    @patch('ptmd.api.queries.users.User')
    @patch('ptmd.api.queries.users.get_jwt', return_value={'sub': 1})
    def test_get_me(self, mock_jwt, mock_user, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        class MockUser:
            def __iter__(self):
                for k, v in {'a': "1", 'b': "2"}.items():
                    yield k, v

        mock_get_current_user().role = 'admin'
        mock_user.query.filter().first.return_value = MockUser()
        with app.test_client() as client:
            response = client.get('/api/users', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.json, {'a': "1", 'b': "2"})
            self.assertEqual(response.status_code, 200)

    def test_login_error(self, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        mock_get_current_user().role = 'admin'
        with app.test_client() as client:
            response = client.post('/api/session',
                                   headers={'Authorization': f'Bearer {123}', **HEADERS},
                                   data=dumps({}))
            self.assertEqual(response.json, {'msg': 'Missing username or password'})

    @patch('ptmd.api.queries.users.TokenBlocklist')
    @patch('ptmd.api.queries.users.get_jwt', return_value={'jti': 1})
    @patch('ptmd.api.queries.users.session')
    def test_logout_user(self, mock_session, mock_jwt, mock_token_blocklist,
                         mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        mock_get_current_user().role = 'admin'
        with app.test_client() as client:
            response = client.delete('/api/session', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.json, {'msg': 'Logout successfully'})

    def test_validate_account(self, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        mock_get_current_user().role = 'admin'
        with patch('ptmd.api.queries.users.User'):
            with app.test_client() as client:
                response = client.get('/api/users/2/activate', headers={'Authorization': f'Bearer {123}', **HEADERS})
                self.assertEqual(response.json, {'msg': 'Account validated'})

    def test_enable_account_errors(self, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        with patch('ptmd.api.queries.users.Token') as mocked_token:
            mocked_token.query.filter().first.return_value.expires_on = datetime.now() - timedelta(days=1)
            with app.test_client() as client:
                response = client.get('/api/users/enable/2', headers={'Authorization': f'Bearer {123}', **HEADERS})
                self.assertEqual(response.json, {'msg': 'Token expired'})
                self.assertEqual(response.status_code, 400)

            mocked_token.query.filter().first.return_value = None
            with app.test_client() as client:
                response = client.get('/api/users/enable/2', headers={'Authorization': f'Bearer {123}', **HEADERS})
                self.assertEqual(response.json, {'msg': 'Invalid token'})
                self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.users.User')
    @patch('ptmd.api.queries.users.Token')
    @patch('ptmd.api.queries.users.enable_account')
    def test_enable_account_success(self, mock_email,
                                    mocked_token, mocked_user,
                                    mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        mocked_token.query.filter().first.return_value.expires_on = datetime.now() + timedelta(days=10)
        mocked_token.query.filter().first.return_value.token = '123'
        with app.test_client() as client:
            response = client.get('/api/users/enable/2', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.json,
                             {'msg': "Account enabled. An email has been to an admin to validate your account."})
