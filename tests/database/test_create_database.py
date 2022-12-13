from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine, engine as sqlengine
from sqlalchemy.orm import sessionmaker, session as sqlsession

from ptmd.database import boot, create_organisations, create_users, Base


class TestCreateDatabase(TestCase):
    engine: sqlengine = None

    def setUp(self) -> None:
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        session: sqlsession = sessionmaker(bind=self.engine)
        self.session = session()
        self.input_orgs = {'KIT': "123", 'UOB': "456"}

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine('sqlite:///:memory:', pool_size=20)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.engine.dispose()

    @patch('ptmd.database.create_database.create_organisations', return_value={'UOX': 1})
    @patch('ptmd.database.create_database.create_users', return_value={'test': 1})
    def test_boot(self, mocked_create_users, mock_create_organisations):
        organisations, users = boot(self.engine, drop_all=False, insert=False)
        self.assertFalse(mocked_create_users.called)
        self.assertFalse(mock_create_organisations.called)
        self.assertEqual(organisations, {})
        self.assertEqual(users, {})

        organisations, users = boot(self.engine, insert=True, drop_all=True)
        self.assertEqual(organisations, mock_create_organisations.return_value)
        self.assertEqual(users, mocked_create_users.return_value)

    def test_create_organisations(self):
        organisations = create_organisations(organisations=self.input_orgs, session=self.session)
        organisations = {org: dict(organisations[org]) for org in organisations}
        self.assertIsNone(organisations['UOX']['gdrive_id'])
        self.assertEqual(organisations['KIT']['gdrive_id'], "123")
        self.assertEqual(organisations['UOB']['gdrive_id'], "456")
        self.session.close()

    def test_create_users(self):
        organisations = create_organisations(organisations=self.input_orgs, session=self.session)
        input_users = [{'username': 'test', 'password': 'test', 'organisation': organisations['KIT']}]
        user = create_users(users=input_users, session=self.session)[0]
        self.assertEqual(
            dict(user),
            {'id': 1, 'username': 'test', 'organisation': {'organisation_id': 1, 'name': 'KIT', 'gdrive_id': '123'}}
        )
        self.session.close()
