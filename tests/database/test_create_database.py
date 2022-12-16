from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine, engine as sqlengine
from sqlalchemy.orm import sessionmaker, session as sqlsession

from ptmd.database import boot, create_organisations, create_users, Base, create_chemicals, create_organisms


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

    @patch('ptmd.database.queries.create_organisations', return_value={'UOX': 1})
    @patch('ptmd.database.queries.create_users', return_value={'test': 1})
    @patch('ptmd.database.queries.create_chemicals', return_value={'test': 1})
    @patch('ptmd.database.queries.create_organisms', return_value={'test': 1})
    def test_boot(self, mock_organisms, mock_chemicals, mocked_create_users, mock_create_organisations):
        organisations, users, chemicals, organisms = boot(session=self.session, insert=False)
        self.assertFalse(mocked_create_users.called)
        self.assertFalse(mock_create_organisations.called)
        self.assertEqual(organisations, {})
        self.assertEqual(users, {})
        self.assertEqual(chemicals, {})
        self.assertEqual(organisms, {})

        organisations, users, chemicals, organisms = boot(session=self.session, insert=True)
        self.assertEqual(organisations, mock_create_organisations.return_value)
        self.assertEqual(users, mocked_create_users.return_value)
        self.assertEqual(chemicals, mock_chemicals.return_value)
        self.assertEqual(organisms, mock_organisms.return_value)

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

    def test_create_chemicals(self):
        chemical_input = [{"common_name": "test", "formula": "test", "name_hash_id": "test", "ptx_code": 1}]
        expected_chemical = {
            'chemical_id': 1, 'common_name': 'test', 'name_hash_id': 'test', 'formula': 'test', 'ptx_code': 1
        }
        chemicals = create_chemicals(chemicals=chemical_input, session=self.session)
        self.assertEqual(dict(chemicals['test']), expected_chemical)
        chemicals = create_chemicals(chemicals=[{"test": 1}], session=self.session)
        self.assertEqual(chemicals, {})

    def test_create_organisms(self):
        organisms_input = [{"scientific_name": "test", "ptox_biosystem_name": "A", "ptox_biosystem_code": "A"}]
        organisms = create_organisms(organisms=organisms_input, session=self.session)
        organism = dict(organisms['A'])
        exp = {'organism_id': 1, 'scientific_name': 'test', 'ptox_biosystem_name': 'A', "ptox_biosystem_code": "A"}
        self.assertEqual(organism, exp)
        organisms = create_organisms(organisms=[{"test": 1}], session=self.session)
        self.assertEqual(organisms, {})
