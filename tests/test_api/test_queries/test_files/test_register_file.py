from unittest import TestCase
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from json import dumps as json_dumps

from ptmd.api import app
from ptmd.database import User, Organisation, Organism, Base


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
new_user = User(**user)
session.add(new_user)
session.commit()

organism = {'ptox_biosystem_name': 'human', 'scientific_name': 'A', 'ptox_biosystem_code': 'B'}
new_organism = Organism(**organism)
session.add(new_organism)
session.commit()


def mock_jwt_required(*args, **kwargs):
    return True


class TestRegisterFile(TestCase):

    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
    @patch('ptmd.api.routes.register_gdrive_file', return_value=({'message': 'File added successfully.'}, 200))
    def test_route(self, mock_validate, mock_jwt):
        with app.test_client() as test_client:
            response = test_client.post('api/files/register')
        self.assertEqual(response.json, {'message': 'File added successfully.'})

    @patch('ptmd.api.queries.files.register.session')
    @patch('ptmd.api.queries.users.session')
    @patch('ptmd.api.queries.files.register.GoogleDriveConnector', return_value=MockGoogleDrive())
    @patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', side_effect=mock_jwt_required)
    @patch('ptmd.api.queries.files.create.get_jwt', return_value={'sub': 1})
    @patch('ptmd.api.queries.files.register.get_jwt', return_value={'sub': 1})
    @patch('ptmd.api.queries.users.login_user', return_value={'access_token': '123'})
    @patch('ptmd.api.queries.files.register.File')
    def test_register_file(self, mock_file, mock_login, mock_jwt_1, mock_jwt_2, mock_verify_jwt, mock_gdrive,
                           mock_session_1, mock_session_2):
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

            with patch('ptmd.api.queries.files.register.jsonify') as mock_jsonify:
                mock_jsonify.return_value = {'data': {'message': 'File added successfully.'}}
                external_file = {'file_id': '123', 'batch': 'AA', 'organism': 'human'}
                file = test_client.post('/api/files/register', headers={'Authorization': f'Bearer {token}', **HEADERS},
                                        data=json_dumps(external_file))
                self.assertEqual(file.json['data']['message'], 'File added successfully.')
                self.assertEqual(file.status_code, 200)
