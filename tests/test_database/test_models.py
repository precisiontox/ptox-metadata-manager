from unittest import TestCase
from unittest.mock import patch

from ptmd.database import User, Organisation, File
from ptmd.database.models.token_blocklist import TokenBlocklist, check_if_token_revoked


class TestUser(TestCase):
    def test_user(self):
        expected_user = {'files': [], 'id': None, 'organisation': None, 'username': 'test'}
        user = User(username='test', password='test', email='your@email.com')
        self.assertEqual(dict(user), expected_user)
        self.assertTrue(user.validate_password('test'))

        with patch('ptmd.database.models.user.session'):
            changed = user.change_password(old_password='test', new_password='test2')
            self.assertTrue(changed)
            changed = user.change_password(old_password='test', new_password='test2')
            self.assertFalse(changed)

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    def test_files(self, mock_organism, mock_organisation):
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        file = File(**{
            'gdrive_id': '123',
            'name': 'test',
            'batch': 'AA',
            'organisation_name': None,
            'user_id': None,
            'organism_name': None})
        self.assertEqual(dict(file), {
            'file_id': None,
            'gdrive_id': '123',
            'name': 'test',
            'batch': 'AA',
            'organisation': None,
            'author': None,
            'organism': None,
        })

    def test_token_block_list(self):
        expired_token = TokenBlocklist(jti='123')
        self.assertTrue(expired_token.jti == "123")

        with patch('ptmd.database.models.token_blocklist.session') as mocked_session:
            mocked_session.query().filter_by().return_value = True
            self.assertTrue(check_if_token_revoked({}, {'jti': '123'}))

    def test_organisation(self):
        expected_organisation = {
            'name': 'UOX', 'organisation_id': None, 'gdrive_id': 'test', 'longname': None, 'files': []
        }
        organisation = Organisation(name=expected_organisation['name'], gdrive_id=expected_organisation['gdrive_id'])
        self.assertEqual(dict(organisation), expected_organisation)

    @patch('ptmd.database.queries.create_access_token', return_value='OK')
    def test_user_with_organisation(self, mock_create_access_token):
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
