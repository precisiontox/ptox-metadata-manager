from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker

from ptmd.config import Base
from ptmd.database import boot, create_organisations, create_users, create_chemicals, create_organisms


mock_empty_data: dict = {
    'organisations': [],
    'users': [],
    'chemicals': [],
    'organisms': []
}


class TestCreateDatabase(TestCase):
    engine: Engine or None = None

    def setUp(self) -> None:
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        session: sessionmaker = sessionmaker(bind=self.engine)
        self.session = session()
        self.input_orgs = {'KIT': {"g_drive": "123", "long_name": "test12"}}

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine('sqlite:///:memory:', pool_size=20)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.engine.dispose()

    @patch('ptmd.database.queries.create_organisations', return_value={'UOX': 1})
    @patch('ptmd.database.queries.create_users', return_value={'test': 1})
    @patch('ptmd.database.queries.create_chemicals', return_value={'test': 1})
    @patch('ptmd.database.queries.create_organisms', return_value={'test': 1})
    def test_boot(self, mock_organisms, mock_chemicals, mocked_create_users, mock_create_organisations):
        organisations, users, chemicals, organisms = boot(insert=False, **mock_empty_data)
        self.assertFalse(mocked_create_users.called)
        self.assertFalse(mock_create_organisations.called)
        self.assertEqual(organisations, {})
        self.assertEqual(users, {})
        self.assertEqual(chemicals, {})
        self.assertEqual(organisms, {})

        organisations, users, chemicals, organisms = boot(insert=True, **mock_empty_data)
        self.assertEqual(organisations, mock_create_organisations.return_value)
        self.assertEqual(users, mocked_create_users.return_value)
        self.assertEqual(chemicals, mock_chemicals.return_value)
        self.assertEqual(organisms, mock_organisms.return_value)

    @patch('ptmd.database.queries.session')
    @patch('ptmd.database.queries.Organisation')
    def test_create_organisations(self, mock_organisation, mock_session):
        mock_organisation.query.filter().first.return_value = self.input_orgs['KIT']
        mock_session.return_value = self.session
        organisations = create_organisations(organisations=self.input_orgs)
        self.assertTrue(mock_session.commit.called)
        self.assertTrue(mock_session.add)
        organisations = {org: dict(organisations[org]) for org in organisations}
        self.assertEqual(organisations['KIT']['g_drive'], "123")
        self.session.close()

    @patch('ptmd.database.queries.session')
    @patch('ptmd.database.queries.Organisation')
    @patch('ptmd.database.queries.User')
    def test_create_users(self, mock_user, mock_organisation, mock_session):
        mock_user.query.filter().first.return_value = 123
        mock_organisation.query.filter().first.return_value = self.input_orgs['KIT']
        mock_session.return_value = self.session
        organisations = create_organisations(organisations=self.input_orgs)
        input_users = [{'username': 'test', 'password': 'test', 'organisation': organisations['KIT']}]
        user = create_users(users=input_users)
        self.assertEqual(user[0], 123)

    def test_create_chemicals(self):
        with patch('ptmd.database.queries.session', self.session):
            chemical_input = [{"common_name": "test", "formula": "test", "name_hash_id": "test", "ptx_code": 1}]
            expected_chemical = {
                'chemical_id': 1, 'common_name': 'test', 'name_hash_id': 'test', 'formula': 'test', 'ptx_code': 1
            }
            chemicals = create_chemicals(chemicals=chemical_input)
            self.assertEqual(dict(chemicals['test']), expected_chemical)
            chemicals = create_chemicals(chemicals=[{"test": 1}])
            self.assertEqual(chemicals, {})

    def test_create_organisms(self):
        with patch('ptmd.database.queries.session', self.session):
            organisms_input = [{"scientific_name": "test", "ptox_biosystem_name": "A", "ptox_biosystem_code": "A"}]
            organisms = create_organisms(organisms=organisms_input)
            organism = dict(organisms['A'])
            exp = {'organism_id': 1, 'scientific_name': 'test', 'ptox_biosystem_name': 'A', "ptox_biosystem_code": "A"}
            self.assertEqual(organism, exp)
            organisms = create_organisms(organisms=[{"test": 1}])
            self.assertEqual(organisms, {})
