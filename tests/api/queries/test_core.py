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

    @patch('ptmd.GoogleDriveConnector.upload_file', return_value=({"id": "45", "title": "test", "alternateLink": "a"}))
    @patch('ptmd.clients.gdrive.core.GoogleAuth', return_value=MockGoogleAuth)
    @patch('ptmd.model.exposure_condition.get_allowed_chemicals', return_value=["chemical1", "chemical2"])
    @patch('ptmd.model.inputs2dataframes.get_allowed_organisms', return_value=['organism1'])
    @patch('ptmd.model.inputs2dataframes.get_organism_code', return_value=['A'])
    @patch('ptmd.model.inputs2dataframes.get_chemical_code_mapping', return_value={'chemical1': '001'})
    def test_create_gdrive_file(self, mock_chemicals_mapping, mock_organism_code,
                                mock_organism, mock_chem, mock_upload, mock_auth,
                                mock_get_session_1, mock_get_session_2, mock_get_session_3):
        organisation = {'name': 'UOB', 'gdrive_id': '456'}
        new_organisation = Organisation(**organisation)
        session.add(new_organisation)
        session.commit()
        organisation = session.query(Organisation).filter_by(name='UOB').first()
        user = {'organisation': organisation, 'username': '123', 'password': '123'}
        new_user = User(**user)
        session.add(new_user)
        organism: Organism = Organism(ptox_biosystem_name="organism1", ptox_biosystem_code="A", scientific_name="human")
        session.add(organism)
        session.commit()

        with app.test_client() as client:
            logged_in = client.post('/api/login', data=dumps({'username': '123', 'password': '123'}), headers=HEADERS)
            jwt = logged_in.json['access_token']
            data = {
                "partner": "UOB",
                "organism": "organism1",
                "exposure_conditions": [{"chemicals_name": ["chemical1"], "dose": "BDM10"}],
                "exposure_batch": "AA",
                "replicate4control": 4,
                "replicate4exposure": 4,
                "replicate_blank": 2,
                "start_date": "2021-01-01",
                "end_date": "2022-01-01",
                "timepoints": 3,
                "vehicle": "water",
            }
            headers = {'Authorization': f'Bearer {jwt}', **HEADERS}
            response = client.post('/api/create_file', headers=headers, data=dumps(data))
            self.assertEqual(response.json["message"],
                             "dose must be one of ['BMD10', 'BMD25', '10mg/L'] but got BDM10")
            self.assertEqual(response.status_code, 400)

            data["exposure_conditions"][0]["dose"] = "BMD10"
            response = client.post('/api/create_file', headers=headers, data=dumps(data))
            self.assertEqual(response.json, {'data': {'file_url': 'a'}})

    def test_get_organisms(self, mock_get_session_1, mock_get_session_2, mock_get_session_3):
        create_user()
        org = {'ptox_biosystem_name': 'organism1', 'scientific_name': 'org1', "ptox_biosystem_code": "A"}
        session.add(Organism(**org))
        session.commit()
        session.close()
        with app.test_client() as client:
            logged_in = client.post('/api/login', data=dumps({'username': '123', 'password': '123'}), headers=HEADERS)
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
            logged_in = client.post('/api/login', data=dumps({'username': '123', 'password': '123'}), headers=HEADERS)
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
            logged_in = client.post('/api/login', data=dumps({'username': '123', 'password': '123'}), headers=HEADERS)
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
