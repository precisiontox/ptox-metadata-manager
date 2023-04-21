from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from json import dumps as json_dumps

from ptmd.api import app
from ptmd.database import Base, User, Organisation, Organism


class MockGoogleDrive:
    def __init__(self, *args, **kwargs):
        pass

    def get_filename(self, *args, **kwargs):
        return 'filename'


engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()
HEADERS = {'Content-Type': 'application/json'}

organisation = {'name': 'UOB'}
new_organisation = Organisation(**organisation)
session.add(new_organisation)
session.commit()

user = {'organisation': new_organisation, 'username': "admin", 'password': 'admin'}
new_user = User(**user, session=session)
session.add(new_user)
session.commit()

organism = {'ptox_biosystem_name': 'human', 'scientific_name': 'A', 'ptox_biosystem_code': 'B'}
new_organism = Organism(**organism)
session.add(new_organism)
session.commit()


class TestRegisterFile(TestCase):

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.routes.register_gdrive_file', return_value=({'message': 'File added successfully.'}, 200))
    def test_route(self, mock_validate, mock_jwt_required):
        with app.test_client() as test_client:
            response = test_client.post('api/files/register')
        self.assertEqual(response.json, {'message': 'File added successfully.'})

    @patch('ptmd.api.queries.files.register.get_session', return_value=session)
    @patch('ptmd.api.queries.users.get_session', return_value=session)
    @patch('ptmd.api.queries.utils.get_session', return_value=session)
    @patch('ptmd.api.queries.files.register.GoogleDriveConnector', return_value=MockGoogleDrive())
    def test_register_file(self, mock_get_session, mock_session_1, moc_session_2, mock_gdrive):
        with app.test_client() as test_client:
            login = test_client.post('/api/session', headers=HEADERS,
                                     data=json_dumps({'username': 'admin', 'password': 'admin'}))
            token = login.json['access_token']

            external_file = {'file_id': '123'}
            file = test_client.post('/api/files/register', headers={'Authorization': f'Bearer {token}', **HEADERS},
                                    data=json_dumps(external_file))
            self.assertEqual(file.json, {'message': 'Field batch is required.'})
            self.assertEqual(file.status_code, 400)

            external_file = {'file_id': '123', 'batch': '2021-01-01', 'organism': 'human'}
            file = test_client.post('/api/files/register', headers={'Authorization': f'Bearer {token}', **HEADERS},
                                    data=json_dumps(external_file))
            self.assertEqual(file.json, {'message': "Batch '2021-01-01' has an incorrect format."})
            self.assertEqual(file.status_code, 400)

            file = test_client.post('/api/files/register', headers={'Authorization': f'Bearer {token}', **HEADERS},
                                    data=json_dumps({}))
            self.assertEqual(file.json, {'message': 'Field file_id is required.'})
            self.assertEqual(file.status_code, 400)

            external_file = {'file_id': '123', 'batch': 'AA', 'organism': 'human'}
            file = test_client.post('/api/files/register', headers={'Authorization': f'Bearer {token}', **HEADERS},
                                    data=json_dumps(external_file))
            self.assertEqual(file.json['data']['message'], 'file 123 was successfully created with internal id 1')
            self.assertEqual(file.status_code, 200)
