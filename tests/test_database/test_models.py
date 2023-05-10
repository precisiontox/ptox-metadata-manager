from unittest import TestCase
from unittest.mock import patch
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ptmd.database import Base
from ptmd.database import User, Organisation, File, login_user
from ptmd.database.models.token_blocklist import TokenBlocklist, check_if_token_revoked


class TestModel(TestCase):

    @classmethod
    def setUpClass(cls):
        engine = create_engine('sqlite:///:memory:', pool_size=20)
        session = sessionmaker(bind=engine)
        cls.session = session()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def test_user(self):
        with patch('ptmd.database.models.user.session', self.session):
            expected_user = {'files': [], 'id': 1, 'organisation': None, 'username': 'test'}
            user = User(username='test', password='test')
            self.session.add(user)
            self.session.commit()
            user_in_db = dict(self.session.query(User).first())
            self.assertEqual(user_in_db, expected_user)
            self.assertTrue(user.validate_password('test'))

            changed = user.change_password(old_password='test', new_password='test2')
            self.assertTrue(changed)
            changed = user.change_password(old_password='test', new_password='test2')
            self.assertFalse(changed)

    def test_organisation(self):
        expected_organisation = {
            'name': 'UOX', 'organisation_id': 1, 'gdrive_id': 'test', 'longname': None, 'files': []
        }
        organisation = Organisation(name=expected_organisation['name'], gdrive_id=expected_organisation['gdrive_id'])
        self.session.add(organisation)
        self.session.commit()
        organisation_in_db = dict(self.session.query(Organisation).first())
        self.assertEqual(organisation_in_db, expected_organisation)

    @patch('ptmd.database.queries.create_access_token', return_value='OK')
    def test_user_with_organisation(self, mock_create_access_token):
        user_input: dict = {'username': 'rw', 'organisation': 123, 'password': 'test'}
        with self.assertRaises(TypeError) as context:
            user = User(**user_input)
            self.session.add(user)
            self.session.commit()
        self.assertEqual(str(context.exception), 'organisation must be an Organisation object or a string')
        organisation: Organisation = Organisation(name=user_input['organisation'], gdrive_id='1')
        self.session.add(organisation)
        self.session.commit()
        user_input['organisation'] = organisation
        user: User = User(**user_input)
        self.session.add(user)
        self.session.commit()
        user_in_db = dict(self.session.query(User).filter_by(username=user_input['username']).first())
        self.assertEqual(user_in_db['username'], user_input['username'])
        self.assertEqual(user_in_db['organisation'], user_input['organisation'].organisation_id)

        class MockOrganisation:
            name: str = "123"

            @staticmethod
            def first() -> object:
                return organisation

        class MockQuery:
            def __init__(self, *args, **kwargs):
                pass

            @staticmethod
            def filter(*args, **kwargs):
                return MockOrganisation()

        with patch('ptmd.database.models.user.Organisation', MockOrganisation) as mock_organisation:
            mock_organisation.query = MockQuery()
            user_input['organisation'] = '123'
            user_input['username'] = 'another user'
            another_user = User(**user_input)
            self.session.add(another_user)
            self.session.commit()
            another_user_in_db = dict(self.session.query(User).filter_by(username=user_input['username']).first())
            self.assertEqual(another_user_in_db['username'], user_input['username'])
            self.assertTrue(another_user_in_db['organisation'])

        with patch('ptmd.database.queries.User') as mock_user:
            with patch('ptmd.database.queries.jsonify', return_value={'access_token': 'OK'}):
                mock_user.query.filter.return_value.first.return_value = user
                logged_in = login_user(user_input['username'], user_input['password'])
                self.assertEqual(logged_in[0], {'access_token': 'OK'})
                self.assertEqual(logged_in[1], 200)

            with patch('ptmd.database.queries.jsonify', return_value={'msg': 'Bad username or password'}):
                mock_user.query.filter.return_value.first.return_value = None
                logged_in = login_user(user_input['username'], 'wrong_password')
                self.assertEqual(logged_in[0], ({"msg": "Bad username or password"}))
                self.assertEqual(logged_in[1], 401)

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
        expired_token = TokenBlocklist(jti='123', created_at=datetime.now(timezone.utc))
        self.session.add(expired_token)
        self.session.commit()
        self.assertTrue(expired_token.id == 1)

        with patch('ptmd.database.models.token_blocklist.session') as mocked_session:
            mocked_session.return_value = self.session
            self.assertTrue(check_if_token_revoked({}, {'jti': '123'}))
