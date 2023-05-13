from unittest import TestCase
from unittest.mock import patch, mock_open

from ptmd.database import User, Organisation, File


@patch("builtins.open", mock_open(read_data="{'save_credentials_file': 'test'}"))
class TestUser(TestCase):

    @patch('ptmd.database.models.token.send_confirmation_mail', return_value=True)
    def test_user(self, mock_send_confirmation_mail):
        expected_user = {'files': [], 'id': None, 'organisation': None, 'username': 'test'}
        user = User(username='test', password='test', email='your@email.com')
        self.assertEqual(dict(user), expected_user)
        self.assertTrue(user.validate_password('test'))

        with patch('ptmd.database.models.user.session') as mock_session:
            changed = user.change_password(old_password='test', new_password='test2')
            self.assertTrue(changed)
            changed = user.change_password(old_password='test', new_password='test2')
            self.assertFalse(changed)

            with patch('ptmd.database.models.user.send_validation_mail') as mock_email:
                user.set_role('enabled')
                self.assertEqual(user.role, 'enabled')
                mock_email.assert_called_once()
                mock_session.commit.assert_called()

            with patch('ptmd.database.models.user.send_validated_account_mail') as mock_mail:
                user.set_role('user')
                self.assertEqual(user.role, 'user')
                mock_mail.assert_called_once_with(username='test', email='your@email.com')
                mock_session.commit.assert_called()

            user.set_role('admin')
            self.assertEqual(user.role, 'admin')

    def test_user_admin(self):
        user = User(username='test', password='test', email='your@email.com', role='admin')
        self.assertEqual(user.role, 'admin')

    @patch('ptmd.database.queries.users.create_access_token', return_value='OK')
    @patch('ptmd.database.models.token.send_confirmation_mail', return_value=True)
    def test_user_with_organisation(self, mock_send_mail, mock_create_access_token):
        organisation: Organisation = Organisation(name='123', gdrive_id='1')
        user_input: dict = {
            'username': 'rw1',
            'organisation_id': organisation.organisation_id,
            'password': 'test',
            'email': 'y@t.com'
        }
        user = User(**user_input)
        self.assertEqual(user.role, 'disabled')
        self.assertEqual(user.username, user_input['username'])
        self.assertEqual(user.organisation_id, user_input['organisation_id'])
