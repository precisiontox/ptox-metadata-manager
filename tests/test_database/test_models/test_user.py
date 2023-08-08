from unittest import TestCase
from unittest.mock import patch, mock_open

from ptmd.database import User, Organisation, File


@patch("builtins.open", mock_open(read_data="{'save_credentials_file': 'test'}"))
class TestUser(TestCase):

    @patch('ptmd.database.models.token.send_confirmation_mail', return_value=True)
    def test_user(self, mock_send_confirmation_mail):
        expected_user = {'files': [], 'id': None, 'organisation': None, 'username': 'test', 'role': 'disabled'}
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
        organisation = Organisation(name='123', gdrive_id='1')
        organisation.files = []
        organisation.id = 2
        user = User(username='test', password='test', email='your@email.com', role='admin')
        user.organisation = organisation
        self.assertEqual(user.role, 'admin')
        self.assertEqual(dict(user)['files'], [])

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

    @patch('ptmd.database.models.user.session')
    @patch('ptmd.database.models.token.send_confirmation_mail', return_value=True)
    def test_set_role_success(self, mock_send_confirmation_mail, mock_session):
        user = User('test', 'test', 'test', 'disabled')
        user.set_role('banned')
        self.assertEqual(user.role, 'banned')
        mock_session.commit.assert_called_once()

    @patch('ptmd.database.models.user.session')
    @patch('ptmd.database.models.token.send_confirmation_mail', return_value=True)
    def test_set_role_invalid_role(self, mock_send_confirmation_mail, mock_session):
        user = User('test', 'test', 'test', 'disabled')
        with self.assertRaises(ValueError) as context:
            user.set_role('invalid role')
        self.assertEqual(str(context.exception), "Invalid role: invalid role")

    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Organisation')
    def test_user_serialisation_with_organisation(self, mock_organisation, mock_organism, mock_chemical):
        file_1 = File(gdrive_id='test', name='test', batch='test', replicates=1, controls=1, blanks=1,
                      organisation_name="org", user_id=1, organism_name='test', vehicle_name="vehicle",
                      start_date='2021-01-01', end_date='2021-01-01')
        file_2 = File(gdrive_id='test2', name='test2', batch='test2', replicates=2, controls=2, blanks=2,
                      organisation_name="org", user_id=2, organism_name='test2', vehicle_name="vehicle2",
                      start_date='2021-01-01', end_date='2021-01-01')
        organisation = Organisation(name='123', gdrive_id='1')
        organisation.files = [file_1, file_2]
        organisation.id = 2
        user = User(username='test', password='test', email='your@email.com', role='admin')
        user.organisation = organisation
        user.files = [file_1]
        files = dict(user)['files']
        self.assertIn(dict(file_1), files)
        self.assertIn(dict(file_2), files)
