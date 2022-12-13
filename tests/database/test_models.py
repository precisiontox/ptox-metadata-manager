from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine, engine as sqlengine
from sqlalchemy.orm import sessionmaker, session as sqlsession

from ptmd.database import Base, User, Organisation, login_user, app


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
        expected_organisation = {'name': 'UOX', 'organisation_id': 1, 'gdrive_id': 'test'}
        organisation = Organisation(name=expected_organisation['name'], gdrive_id=expected_organisation['gdrive_id'])
        self.session.add(organisation)
        self.session.commit()
        organisation_in_db = dict(self.session.query(Organisation).first())
        self.assertEqual(organisation_in_db, expected_organisation)

    @patch('ptmd.database.models.create_access_token', return_value='OK')
    def test_user_with_organisation(self, mock_create_access_token):
        user_input = {'username': 'rw', 'organisation': 'UOB', 'password': 'test'}
        with self.assertRaises(TypeError) as context:
            user = User(**user_input)
            self.session.add(user)
            self.session.commit()
        self.assertEqual(str(context.exception), 'organisation must be an Organisation object')
        organisation = Organisation(name=user_input['organisation'], gdrive_id='test_id')
        user_input['organisation'] = organisation
        user = User(**user_input)
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
