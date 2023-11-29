from unittest import TestCase
from unittest.mock import patch
from datetime import datetime, timedelta

from ptmd.database.queries import login_user, create_organisations, create_users, get_token
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

    @patch('ptmd.database.queries.users.create_access_token', return_value='ABC')
    @patch('ptmd.database.queries.users.jsonify')
    @patch('ptmd.database.queries.users.User')
    def test_login_user_success(self, mock_user, mock_jsonify, mock_access_token):
        mock_user.query.filter().first.return_value = MockModel()
        response = login_user('A', 'B')
        mock_jsonify.assert_called_once_with(access_token='ABC')
        self.assertEqual(response[1], 200)

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
    def test_get_token(self, mock_token):
        mock_token.query.filter().first.return_value = None
        with self.assertRaises(TokenInvalidError) as context:
            get_token('ABC')
        self.assertEqual(str(context.exception), 'Invalid token')

        class MockToken:
            def __init__(self):
                self.expires_on = datetime.now() - timedelta(days=10)

        mock_token.query.filter().first.return_value = MockToken()
        with self.assertRaises(TokenExpiredError) as context:
            get_token('ABC')
        self.assertEqual(str(context.exception), 'Token expired')