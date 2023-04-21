from unittest import TestCase
from unittest.mock import patch
from json import dumps

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session
from pydrive2.auth import GoogleAuth

from ptmd.api import app
from ptmd.database import Base, User, Organisation, Organism, Chemical


engine = create_engine("sqlite://", poolclass=StaticPool)
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()
HEADERS = {'Content-Type': 'application/json'}


class MockGoogleAuth(GoogleAuth):
    credentials = None
    access_token_expired = True

    def LoadCredentialsFile(*args, **kwargs):
        pass

    def LocalWebserverAuth(*args, **kwargs):
        pass

    def SaveCredentialsFile(*args, **kwargs):
        pass

    def Refresh(*args, **kwargs):
        pass

    def Authorize(*args, **kwargs):
        pass

    def SaveCredentials(self, backend=None):
        pass


@patch('ptmd.api.queries.core.get_session', return_value=session)
@patch('ptmd.api.queries.users.get_session', return_value=session)
@patch('ptmd.api.queries.utils.get_session', return_value=session)
class TestCoreQueries(TestCase):
    session: Session or None = None

    def setUp(self) -> None:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def test_get_organisms(self, mock_get_session_1, mock_get_session_2, mock_get_session_3):
        create_user()
        org = {'ptox_biosystem_name': 'organism1', 'scientific_name': 'org1', "ptox_biosystem_code": "A"}
        session.add(Organism(**org))
        session.commit()
        session.close()
        with app.test_client() as client:
            logged_in = client.post('/api/session', data=dumps({'username': '123', 'password': '123'}), headers=HEADERS)
            jwt = logged_in.json['access_token']
            response = client.get('/api/organisms', headers={'Authorization': f'Bearer {jwt}'})
            data = response.json
            expected_organism = {'organism_id': 1, 'ptox_biosystem_name': 'organism1', 'scientific_name': 'org1',
                                 "ptox_biosystem_code": "A"}
            self.assertEqual(data['data'], [expected_organism])
            self.assertEqual(response.status_code, 200)

    def test_get_organisations(self, mock_get_session_1, mock_get_session_2, mock_get_session_3):
        create_user()
        organisation = {'name': 'UOB', 'gdrive_id': '456', 'longname': 'University of Birmingham', 'files': []}
        session.add(Organisation(**organisation))
        session.commit()
        session.close()
        with app.test_client() as client:
            logged_in = client.post('/api/session', data=dumps({'username': '123', 'password': '123'}), headers=HEADERS)
            jwt = logged_in.json['access_token']
            response = client.get('/api/organisations', headers={'Authorization': f'Bearer {jwt}'})
            data = response.json
            self.assertEqual(data['data'], [{**organisation, 'organisation_id': 1}])

    def test_get_chemicals(self, mock_get_session_1, mock_get_session_2, mock_get_session_3):
        create_user()
        chemical = {'common_name': 'chemical1', 'name_hash_id': '123', 'formula': 'C1H1', "ptx_code": 1}
        session.add(Chemical(**chemical))
        session.commit()
        session.close()
        with app.test_client() as client:
            logged_in = client.post('/api/session', data=dumps({'username': '123', 'password': '123'}), headers=HEADERS)
            jwt = logged_in.json['access_token']
            response = client.get('/api/chemicals', headers={'Authorization': f'Bearer {jwt}'})
            data = response.json
            expected_chemical = {'chemical_id': 1, 'common_name': 'chemical1',
                                 'formula': 'C1H1', 'name_hash_id': '123', 'ptx_code': 1}
            self.assertEqual(data["data"], [expected_chemical])


def create_user():
    user = {'organisation': None, 'username': '123', 'password': '123'}
    new_user = User(**user)
    session.add(new_user)
    session.commit()
    return new_user
