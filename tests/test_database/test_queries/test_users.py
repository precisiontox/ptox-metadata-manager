from unittest import TestCase
from unittest.mock import patch
from datetime import datetime, timedelta

from ptmd.database.queries import login_user, create_organisations, create_users, get_token, email_admins_file_shipped
from ptmd.exceptions import TokenInvalidError, TokenExpiredError

INPUTS_ORGS = {'KIT': {"g_drive": "123", "long_name": "test12"}}


class MockModel:
    @staticmethod
    def validate_password(password):
        return True

    def __iter__(self):
        for k, v in {"id": 1}.items():
            yield k, v


class TestUsersQueries(TestCase):

    @patch('ptmd.database.queries.users.jsonify')
    @patch('ptmd.database.queries.users.User')
    def test_login_user_error(self, mock_user, mock_jsonify):
        mock_user.query.filter().first.return_value = None
        response = login_user('A', 'B')
        mock_jsonify.assert_called_once_with({'msg': 'Bad username or password'})
        self.assertEqual(response[1], 401)

    @patch('ptmd.database.queries.users.jsonify')
    @patch('ptmd.database.queries.users.User')
    @patch('ptmd.database.queries.users.session')
    def test_login_user_success(self, mock_session, mock_user, mock_jsonify):
        mock_user.query.filter.return_value.first.return_value.login.return_value = ('JTI', 'JWT')
        response = login_user('A', 'B')
        mock_session.add.assert_called_once_with('JTI')
        self.assertEqual(response[1], 200)
        mock_jsonify.assert_called_once_with({'access_token': 'JWT'})

    @patch('ptmd.database.queries.users.session')
    @patch('ptmd.database.queries.organisations.session')
    @patch('ptmd.database.queries.organisations.Organisation')
    @patch('ptmd.database.queries.users.User')
    def test_create_users(self, mock_user, mock_organisation, mock_users_session, mock_org_session):
        mock_user.query.filter().first.return_value = 123
        mock_organisation.query.filter().first.return_value = INPUTS_ORGS['KIT']
        organisations = create_organisations(organisations=INPUTS_ORGS)
        input_users = [{'username': 'test', 'password': 'test', 'organisation': organisations['KIT']}]
        user = create_users(users=input_users)
        self.assertEqual(user[0], 123)

    @patch('ptmd.database.queries.users.Token')
    @patch('ptmd.database.queries.users.session.delete')
    @patch('ptmd.database.queries.users.session.commit')
    def test_get_token(self, mock_session_commit, mock_session_delete, mock_token):
        mock_token.query.filter().first.return_value = None
        with self.assertRaises(TokenInvalidError) as context:
            get_token('ABC')
            mock_session_delete.assert_not_called()
            mock_session_commit.assert_not_called()
        self.assertEqual(str(context.exception), 'Invalid token')

        class MockToken:
            def __init__(self):
                self.expires_on = datetime.now() - timedelta(days=10)

        mock_token.query.filter().first.return_value = MockToken()
        with self.assertRaises(TokenExpiredError) as context:
            get_token('ABC')
            mock_session_delete.assert_called_once_with(mock_token.query.filter().first())
            mock_session_commit.assert_called_once()
        self.assertEqual(str(context.exception), 'Token expired')

    @patch('ptmd.database.queries.users.User')
    @patch('ptmd.database.queries.users.send_file_shipped_email')
    def test_email_admins_file_shipped(self, mock_email, mock_user):
        class MockedUser:
            def __init__(self):
                self.email = "test@test.com"

        mock_email.return_value = 'test@test.org'
        mock_user.query.filter.return_value = [MockedUser()]
        email = email_admins_file_shipped('FILENAME')
        self.assertEqual(email, 'test@test.org')
        mock_email.assert_called_once_with('FILENAME', ['test@test.com'])
        mock_user.query.filter.assert_called_once_with(False)
