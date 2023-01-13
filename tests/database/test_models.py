from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine, engine as sqlengine
from sqlalchemy.orm import sessionmaker, session as sqlsession

from ptmd.database import Base, User, Organisation, File, login_user, app


class TestModel(TestCase):
    engine: sqlengine = None
    session: sqlsession = None

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine('sqlite:///:memory:', pool_size=20)
        Base.metadata.drop_all(cls.engine)
        Base.metadata.create_all(cls.engine)
        session = sessionmaker(bind=cls.engine)
        cls.session = session()

    @classmethod
    def tearDownClass(cls):
        cls.session.close()
        cls.engine.dispose()

    def test_user(self):
        expected_user = {'username': 'test', 'id': 1, 'organisation': None}
        user = User(username='test', password='test')
        self.session.add(user)
        self.session.commit()
        user_in_db = dict(self.session.query(User).first())
        self.assertEqual(user_in_db, expected_user)
        self.assertTrue(user.validate_password('test'))

        changed = user.change_password(old_password='test', new_password='test2', session=self.session)
        self.assertTrue(changed)
        changed = user.change_password(old_password='test', new_password='test2', session=self.session)
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

    def test_chemical(self):
        pass

    def test_organism(self):
        pass

    @patch('ptmd.database.queries.create_access_token', return_value='OK')
    def test_user_with_organisation(self, mock_create_access_token):
        user_input: dict = {'username': 'rw', 'organisation': 123, 'password': 'test'}
        with self.assertRaises(TypeError) as context:
            user = User(**user_input, session=self.session)
            self.session.add(user)
            self.session.commit()
        self.assertEqual(str(context.exception), 'organisation must be an Organisation object or a string')
        organisation: Organisation = Organisation(name=user_input['organisation'], gdrive_id='test_id')
        user_input['organisation'] = organisation
        user: User = User(**user_input)
        self.session.add(user)
        self.session.commit()
        user_in_db = dict(self.session.query(User).filter_by(username=user_input['username']).first())
        self.assertEqual(user_in_db['username'], user_input['username'])
        self.assertEqual(user_in_db['organisation']['name'], user_input['organisation'].name)
        self.assertEqual(user_in_db['organisation']['gdrive_id'], user_input['organisation'].gdrive_id)

        with app.app_context():
            logged_in = login_user(user_input['username'], user_input['password'], self.session)
            self.assertEqual(logged_in[0].json, {'access_token': 'OK'})
            self.assertEqual(logged_in[1], 200)

            logged_in = login_user(user_input['username'], 'wrong_password', self.session)
            self.assertEqual(logged_in[0].json, ({"msg": "Bad username or password"}))
            self.assertEqual(logged_in[1], 401)

        user_input['organisation'] = 'test'
        with self.assertRaises(ValueError) as context:
            User(**user_input)
        self.assertEqual("session must be provided if organisation is a string", str(context.exception))
        user = User(**user_input, session=self.session)
        self.assertIsNone(user.organisation)

    def test_files(self):
        file = File(**{
            'gdrive_id': '123',
            'name': 'test',
            'batch': 'AA',
            'organisation_name': None,
            'user_id': None,
            'organism_name': None,
        }, session=self.session)
        self.assertEqual(dict(file), {
            'file_id': None,
            'gdrive_id': '123',
            'name': 'test',
            'batch': 'AA',
            'organisation': None,
            'author': None,
            'organism': None,
        })
