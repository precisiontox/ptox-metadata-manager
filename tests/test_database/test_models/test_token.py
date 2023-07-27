from unittest import TestCase
from unittest.mock import patch

from ptmd.database.models import Token


class MockedUser:
    def __init__(self):
        self.username = 'test'
        self.email = 'test@mail.com'


class TestToken(TestCase):

    @patch('ptmd.database.models.token.send_confirmation_mail')
    def test_activation_token(self, mock_mail):
        token = Token(token_type='activation', user=MockedUser())
        self.assertEqual(token.token_type, 'activation')
        mock_mail.assert_called_with(username='test', email='test@mail.com', token=token.token)

    @patch('ptmd.database.models.token.send_reset_pwd_email')
    def test_reset_token(self, mock_mail):
        token = Token(token_type='reset', user=MockedUser())
        self.assertEqual(token.token_type, 'reset')
        mock_mail.assert_called_with(username='test', email='test@mail.com', token=token.token)

    def test_token_error(self):
        with self.assertRaises(ValueError) as context:
            Token(token_type='invalid', user=MockedUser())
        self.assertEqual('Invalid token type: invalid; must be either "activation" or "reset"', str(context.exception))
