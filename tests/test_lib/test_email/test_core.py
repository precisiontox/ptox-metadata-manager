from unittest import TestCase
from unittest.mock import patch

from ptmd.lib.email.core import send_validation_mail, send_validated_account_mail, send_reset_pwd_email
from ptmd.database.models import User


@patch('ptmd.lib.email.core.Credentials')
@patch('ptmd.lib.email.core.get_config', return_value=True)
@patch('ptmd.lib.email.core.build')
class TestEmailCore(TestCase):

    def test_send_validation_mail(self, mock_build, mock_get_config, mock_credentials):
        user = User(username='username', email='email', password='!Str0?nkPassw0rd')
        response = send_validation_mail(user)
        self.assertIn('<h1> Hello, admin </h1>', response)

    def test_send_validated_account_mail(self, mock_build, mock_get_config, mock_credentials):
        response = send_validated_account_mail('username', 'email')
        self.assertIn('<h1> Hello, username </h1>', response)
        self.assertNotIn('email', response)

    def test_send_reset_pwd_email(self, mock_build, mock_get_config, mock_credentials):
        response = send_reset_pwd_email('username', 'email@test.com', 'token')
        self.assertIn('<h1> Hello, username </h1>', response)
        self.assertIn('token', response)
        self.assertNotIn('email@test.com', response)

