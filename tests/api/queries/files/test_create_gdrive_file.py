from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, Session
from pydrive2.auth import GoogleAuth
from json import dumps

from ptmd.api import app
from ptmd.const import ALLOWED_DOSE_VALUES
from ptmd.database import Base, User, Organisation, Organism


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


engine = create_engine("sqlite://", poolclass=StaticPool)
Base.metadata.create_all(engine)
session: Session = sessionmaker(bind=engine)()
HEADERS = {'Content-Type': 'application/json'}


@patch('ptmd.api.queries.users.get_session', return_value=session)
@patch('ptmd.api.queries.utils.get_session', return_value=session)
@patch('ptmd.api.queries.files.create.get_session', return_value=session)
class TestCreateFile(TestCase):

    @patch('ptmd.GoogleDriveConnector.upload_file', return_value=({"id": "45", "title": "test", "alternateLink": "a"}))
    @patch('ptmd.lib.gdrive.core.GoogleAuth', return_value=MockGoogleAuth)
    @patch('ptmd.lib.creator.core.get_chemical_code_mapping', return_value={"chemical1": '001'})
    @patch('ptmd.lib.creator.core.get_allowed_organisms', return_value=['organism1'])
    @patch('ptmd.lib.creator.core.get_organism_code', return_value=['A'])
    @patch('ptmd.lib.creator.core.get_chemical_code_mapping', return_value={'chemical1': '001'})
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
                "exposure_conditions": [{"chemicals": ["chemical1"], "dose": "BDM10"}],
                "exposure_batch": "AA",
                "replicate4control": 4,
                "replicate4exposure": 4,
                "replicate_blank": 2,
                "start_date": "2021-01-01",
                "end_date": "2022-01-01",
                "timepoints": [3],
                "vehicle": "water",
            }
            headers = {'Authorization': f'Bearer {jwt}', **HEADERS}
            response = client.post('/api/create_file', headers=headers, data=dumps(data))
            self.assertEqual(response.json["message"],
                             f"'exposure' value 'BDM10' is not one of {ALLOWED_DOSE_VALUES}")
            self.assertEqual(response.status_code, 400)

            data["exposure_conditions"][0]["dose"] = "BMD10"
            response = client.post('/api/create_file', headers=headers, data=dumps(data))
            self.assertEqual(response.json, {'data': {'file_url': 'a'}})
