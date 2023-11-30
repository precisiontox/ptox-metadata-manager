from unittest import TestCase
from unittest.mock import patch
from json import dumps
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError

from ptmd.api import app
from ptmd.exceptions import PasswordPolicyError, TokenInvalidError, TokenExpiredError


HEADERS = {'Content-Type': 'application/json'}


class MockedFile:
    def __init__(self):
        self.author = 'author'


class MockedUser:
    def __init__(self) -> None:
        self.role = "enabled"
        self.id = 2
        self.files = [MockedFile()]

    def set_role(self, role):
        self.role = role


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
    @patch('ptmd.api.queries.users.Organisation')
    def test_create_user(self, mock_organisation, mock_user,
                         mock_session, mock_get_current_user,
                         mock_verify_jwt, mock_verify_in_request):
        mock_get_current_user().role = 'admin'
        mock_organisation.query.filter.return_value.first.organisation_id = 1
        mock_user.return_value = {'id': None, 'username': '1234', 'organisation': None, 'files': []}
        user_data = {
            "username": "1234",
            "password": "1234",
            "confirm_password": "1234",
            "organisation": "UOX",
            "email": "t@t.com"
        }
        with app.test_client() as client:
            client.post('/api/users', headers={'Authorization': f'Bearer {123}', **HEADERS},
                        data=dumps(user_data))
            user_data['confirm_password'] = None
            created_user = client.post('/api/users',
                                       headers={'Authorization': f'Bearer {123}', **HEADERS},
                                       data=dumps(user_data))
            self.assertEqual(created_user.json['msg'],
                             {'error': "None is not of type 'string'", 'field': 'confirm_password'})

            user_data['confirm_password'] = '124'
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
            self.assertEqual(created_user.json, {'msg': 'Username or email already taken'})

    @patch('ptmd.api.queries.users.Organisation')
    def test_create_user_invalid_password(
            self, mock_organisation, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        mock_get_current_user().role = 'admin'
        user_data = {
            "username": "1234",
            "password": "1234",
            "confirm_password": "1234",
            "organisation": "UOX",
            "email": "test@test.com"
        }
        with app.test_client() as client:
            response = client.post('/api/users', headers={'Authorization': f'Bearer {123}', **HEADERS},
                                   data=dumps(user_data))
            self.assertEqual(response.json, {'msg': 'Password must be between 8 and 20 characters long, contain at '
                                                    'least one uppercase letter, one lowercase letter, one number '
                                                    'and one special character.'})
            self.assertEqual(response.status_code, 400)

            user_data['password'] = '!@#$%a^&A()a'
            user_data['confirm_password'] = '!@#$%a^&A()a'
            mock_organisation.query.filter.side_effect = Exception
            response = client.post('/api/users', headers={'Authorization': f'Bearer {123}', **HEADERS},
                                   data=dumps(user_data))
            self.assertEqual(response.json, {'msg': 'An unexpected error occurred'})
            self.assertEqual(response.status_code, 500)

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
            created_user = client.put('/api/users',
                                      headers={'Authorization': f'Bearer {123}', **HEADERS},
                                      data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': 'New password cannot be the same as the old one'})

            user_data['confirm_password'] = '666'
            user_data['new_password'] = '666'
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

            mock_user.query.filter().first().change_password.side_effect = PasswordPolicyError()
            mock_get_current_user().role = 'admin'
            created_user = client.put('/api/users',
                                      headers={'Authorization': f'Bearer {123}', **HEADERS},
                                      data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': "Password must be between 8 and 20 characters long, contain at "
                                                        "least one uppercase letter, one lowercase letter, one number "
                                                        "and one special character."})
            self.assertEqual(created_user.status_code, 400)

            mock_user.query.filter().first().change_password = lambda x: x/0
            created_user = client.put('/api/users',
                                      headers={'Authorization': f'Bearer {123}', **HEADERS},
                                      data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': 'An unexpected error occurred'})
            self.assertEqual(created_user.status_code, 500)

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
            response = client.get('/api/user', headers={'Authorization': f'Bearer {123}', **HEADERS})
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
        with patch('ptmd.database.queries.users.Token') as mocked_token:
            mocked_token.query.filter().first.return_value.expires_on = datetime.now() - timedelta(days=11)
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
    @patch('ptmd.database.queries.users.Token')
    @patch('ptmd.api.queries.users.enable_account')
    @patch('ptmd.api.queries.users.session')
    def test_enable_account_success(self, mock_session, mock_email,
                                    mocked_token, mocked_user,
                                    mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        mocked_token.query.filter().first.return_value.expires_on = datetime.now() + timedelta(days=1)
        mocked_token.query.filter().first.return_value.token = '123'
        with app.test_client() as client:
            response = client.get('/api/users/enable/2', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.json,
                             {'msg': "Account enabled. An email has been to an admin to validate your account."})
            self.assertEqual(response.status_code, 200)

    @patch('ptmd.api.queries.users.User')
    def test_get_users(self, mock_users, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):

        class MockedUser:
            def __init__(self) -> None:
                self.id = 1
                self.username = 'test'
                self.organisation = None
                self.role = 'admin'
                self.email = ''
                self.files: list = []

        mock_get_current_user().role = 'admin'
        mock_users.query.all.return_value = [MockedUser()]
        expected_user = {'id': 1, 'username': 'test', 'organisation': None, 'role': 'admin', 'email': '', 'files': []}
        with app.test_client() as client:
            response = client.get('/api/users', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.json, [expected_user])

    def test_send_reset_email_failed(self, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        with app.test_client() as client:
            response = client.post('/api/users/request_reset', data=dumps({}), headers=headers)
            self.assertEqual(response.json, {'msg': 'Missing email'})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.users.User')
    def test_send_reset_email_success_no_user(self, mock_user,
                                              mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        mock_user.query.filter().first.return_value = None
        with app.test_client() as client:
            response = client.post('/api/users/request_reset', data=dumps({"email": "test"}), headers=headers)
            self.assertEqual(response.json, {'msg': 'Email sent'})
            self.assertEqual(response.status_code, 200)

    @patch('ptmd.api.queries.users.User')
    @patch('ptmd.api.queries.users.Token')
    @patch('ptmd.api.queries.users.session')
    def test_send_reset_email_success(self, mock_session, mock_token, mock_user,
                                      mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        mock_user.query.filter().first.return_value.reset_token = '123'
        mock_token.return_value.token = '456'
        with app.test_client() as client:
            response = client.post('/api/users/request_reset', data=dumps({"email": "test"}), headers=headers)
            self.assertEqual(response.json, {'msg': 'Email sent'})
            self.assertEqual(response.status_code, 200)
            mock_session.add.assert_called_with(mock_user.query.filter().first.return_value)
            mock_session.commit.assert_called_once()

    def test_reset_password_failed(self, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        with app.test_client() as client:
            response = client.post('/api/users/reset/123', data=dumps({}), headers=headers)
            self.assertEqual(response.json, {"msg": "Missing password"})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.users.get_token')
    def test_reset_password_error(self, mock_token,
                                  mock_get_current_user, mock_verify_jwt, mock_verify_in_request):

        mock_token.return_value.user_reset[0].set_password.side_effect = PasswordPolicyError
        headers = {'Authorization': f'Bearer 123', **HEADERS}
        with app.test_client() as client:
            response = client.post('/api/users/reset/456', data=dumps({"password": "None"}), headers=headers)
            self.assertEqual(response.json, {"msg": "Password must be between 8 and 20 characters long, contain at "
                                                    "least one uppercase letter, one lowercase letter, one number "
                                                    "and one special character."})
            self.assertEqual(response.status_code, 400)

            mock_token.side_effect = TokenInvalidError
            response = client.post('/api/users/reset/123', data=dumps({"password": "None"}), headers=headers)
            self.assertEqual(response.json, {"msg": "Invalid token"})
            self.assertEqual(response.status_code, 400)

            mock_token.side_effect = TokenExpiredError
            response = client.post('/api/users/reset/123', data=dumps({"password": "None"}), headers=headers)
            self.assertEqual(response.json, {"msg": "Token expired"})
            self.assertEqual(response.status_code, 400)

            mock_token.side_effect = Exception
            response = client.post('/api/users/reset/123', data=dumps({"password": "None"}), headers=headers)
            self.assertEqual(response.json, {"msg": "An unexpected error occurred"})
            self.assertEqual(response.status_code, 500)

    @patch('ptmd.api.queries.users.get_token')
    @patch('ptmd.api.queries.users.session')
    def test_reset_password_success(self, mock_session, mock_token,
                                    mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        class MockedUser:
            def __init__(self) -> None:
                self.pwd = None

            def set_password(self, pwd):
                self.pwd = pwd

        mocked_user: MockedUser = MockedUser()
        mock_token.return_value.user_reset = [mocked_user]
        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        with app.test_client() as client:
            response = client.post('/api/users/reset/123', data=dumps({"password": "None"}), headers=headers)
            self.assertEqual(response.json, {"msg": "Password changed successfully"})
            self.assertEqual(response.status_code, 200)
            mock_session.delete.assert_called_with(mock_token.return_value)
            self.assertEqual(mocked_user.pwd, "None")

    @patch('ptmd.api.queries.users.User')
    @patch('ptmd.api.queries.users.session')
    @patch('ptmd.api.queries.users.get_current_user')
    def test_make_admin_success(self, mock_current_user, mock_session, mock_user,
                                mock_get_current_user_utils, mock_verify_jwt, mock_verify_in_request):

        mock_get_current_user_utils.return_value.role = 'admin'
        mock_user.query.filter().return_value = MockedUser()
        mock_current_user.return_value = MockedUser()
        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        with app.test_client() as client:
            response = client.get('/api/users/2/make_admin', headers=headers)
            self.assertEqual(response.json, {"msg": "User 2 role has been changed to admin"})
            self.assertEqual(response.status_code, 200)

    @patch('ptmd.api.queries.users.User')
    def test_make_admin_failed_404(self, mock_user, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        mock_user.query.filter().first.return_value = None
        mock_get_current_user.return_value.role = 'admin'
        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        with app.test_client() as client:
            response = client.get('/api/users/100/make_admin', headers=headers)
            self.assertEqual(response.json, {"msg": "User not found"})
            self.assertEqual(response.status_code, 404)

    @patch('ptmd.api.queries.users.User')
    @patch('ptmd.api.queries.users.get_current_user')
    def test_make_admin_failed_change_self(self, mock_get_current_user, mock_user,
                                           mock_get_current_user_utils, mock_verify_jwt, mock_verify_in_request):
        mock_user.query.filter().first.return_value.id = 1
        mock_get_current_user_utils.return_value.role = 'admin'
        mock_get_current_user.return_value.id = 1
        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        with app.test_client() as client:
            response = client.get('/api/users/1/make_admin', headers=headers)
            self.assertEqual(response.json, {"msg": "Cannot change your own role"})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.users.User')
    @patch('ptmd.api.queries.users.session')
    @patch('ptmd.api.queries.users.get_current_user')
    def test_make_admin_failed_invalid_role(self, mock_current_user, mock_session, mock_user,
                                            mock_get_current_user_utils, mock_verify_jwt, mock_verify_in_request):
        mock_get_current_user_utils.return_value.role = 'admin'
        mock_get_current_user_utils.return_value.role = 'admin'
        mock_user.query.filter().return_value = MockedUser()
        mock_current_user.return_value = MockedUser()
        mock_user.query.filter().first.return_value.set_role.side_effect = ValueError()

        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        with app.test_client() as client:
            response = client.get('/api/users/2/make_admin', headers=headers)
            self.assertEqual(response.json, {'msg': 'Invalid role'})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.users.User')
    @patch('ptmd.api.queries.users.session')
    @patch('ptmd.api.queries.users.get_current_user')
    def test_ban_success(self, mock_current_user, mock_session, mock_user,
                         mock_get_current_user_utils, mock_verify_jwt, mock_verify_in_request):
        mock_get_current_user_utils.return_value.role = 'admin'
        mock_user.query.filter().return_value = MockedUser()
        mock_current_user.return_value = MockedUser()
        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        with app.test_client() as client:
            response = client.get('/api/users/2/ban', headers=headers)
            self.assertEqual(response.json, {"msg": "User 2 role has been changed to banned"})
            self.assertEqual(response.status_code, 200)

    @patch('ptmd.api.queries.users.User')
    @patch('ptmd.api.queries.users.session')
    @patch('ptmd.api.queries.users.get_current_user')
    def test_delete_user_success(self, mock_current_user, mock_session, mock_user,
                                 mock_get_current_user_utils, mock_verify_jwt, mock_verify_in_request):
        mock_get_current_user_utils.return_value.role = 'admin'

        mocked_user: MockedUser = MockedUser()
        mocked_user.id = 3
        mocked_user.role = 'admin'

        mock_user.query.filter().first.return_value = mocked_user
        mock_current_user.return_value = mocked_user

        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        with app.test_client() as client:
            response = client.delete('/api/users/2', headers=headers)
            self.assertEqual(response.json, {"msg": "User 2 deleted"})
            self.assertEqual(response.status_code, 200)
            mock_session.delete.assert_called_with(mock_user.query.filter().first.return_value)

    @patch('ptmd.api.queries.users.User')
    @patch('ptmd.api.queries.users.session')
    @patch('ptmd.api.queries.users.get_current_user')
    def test_delete_user_failed_404(self, mock_current_user, mock_session, mock_user,
                                    mock_get_current_user_utils, mock_verify_jwt, mock_verify_in_request):
        mock_user.query.filter().first.return_value = None
        headers = {'Authorization': f'Bearer {123}', **HEADERS}
        with app.test_client() as client:
            response = client.delete('/api/users/2', headers=headers)
            self.assertEqual(response.json, {"msg": "User not found"})
            self.assertEqual(response.status_code, 404)

    @patch('ptmd.api.queries.users.User')
    @patch('ptmd.api.queries.users.session')
    @patch('ptmd.api.queries.users.get_current_user')
    def test_delete_user_failed_401(self, mock_current_user, mock_session, mock_user,
                                    mock_get_current_user_utils, mock_verify_jwt, mock_verify_in_request):
        mock_user.query.filter().first.return_value.id = 3
        mock_current_user.return_value.id = 5
        mock_current_user.return_value.role = "user"
        with app.test_client() as client:
            response = client.delete('/api/users/2', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.json, {"msg": "Unauthorized"})
            self.assertEqual(response.status_code, 401)

    @patch('ptmd.api.queries.users.User')
    @patch('ptmd.api.queries.users.session')
    @patch('ptmd.api.queries.users.get_current_user')
    def test_delete_user_failed_400(self, mock_current_user, mock_session, mock_user,
                                    mock_get_current_user_utils, mock_verify_jwt, mock_verify_in_request):
        mock_user.query.filter().first.return_value.id = 1
        mock_current_user.return_value.id = 1
        mock_current_user.return_value.role = "user"
        with app.test_client() as client:
            response = client.delete('/api/users/1', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.json, {"msg": "Cannot delete super user"})
            self.assertEqual(response.status_code, 400)

    def test_token(self, mock_get_current_user, mock_verify_jwt, mock_verify_in_request):
        with app.test_client() as client:
            response = client.get('/api/session', headers={'Authorization': f'Bearer {123}', **HEADERS})
            self.assertEqual(response.status_code, 200)
