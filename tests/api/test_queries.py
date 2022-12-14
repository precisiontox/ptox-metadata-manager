from unittest import TestCase
from unittest.mock import patch
from json import dumps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from flask_jwt_extended import create_access_token

from ptmd.api import app
from ptmd.database import Base, User, Organisation


engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()
HEADERS = {'Content-Type': 'application/json'}


@patch('ptmd.api.queries.get_session', return_value=session)
class TestAPIQueries(TestCase):
    session: Session or None = None

    def setUp(self) -> None:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def test_login_failure(self, mock_get_session):
        with app.test_client() as client:
            response = client.post('/api/login', data=dumps({}), headers=HEADERS)
            self.assertEqual(response.json, {"msg": "Missing username or password"})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.login_user', return_value=({"msg": "hello !"}, 200))
    def test_login_success(self, mock_session, mock_login_user):
        with app.test_client() as client:
            response = client.post('/api/login', headers=HEADERS,
                                   data=dumps({'username': '123', 'password': '123'}))
            self.assertEqual(response.json, {'msg': 'hello !'})
            self.assertEqual(response.status_code, 200)

    def test_get_me(self, mock_get_session):
        user = {'organisation': None, 'username': '123', 'password': '123'}
        new_user = User(**user)
        session.add(new_user)
        session.commit()
        with app.test_client() as client:
            logged_in = client.post('/api/login', data=dumps({'username': '123', 'password': '123'}), headers=HEADERS)
            jwt = logged_in.json['access_token']
            response = client.get('/api/me', headers={'Authorization': f'Bearer {jwt}'})
            self.assertEqual(response.json, {'id': 1, 'organisation': None, 'username': '123'})
            self.assertEqual(response.status_code, 200)

            jwt_data = {'fresh': False, 'iat': 1671016843, 'jti': '8e7c5c51-11b0-4e09-80b7-751debff5a79',
                        'type': 'access', 'sub': 2, 'nbf': 1671016843, 'exp': 88071016843}
            jwt = create_access_token(identity=jwt_data)
            response = client.get('/api/me', headers={'Authorization': f'Bearer {jwt}'})
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json, {'msg': 'Invalid token'})

    @patch('ptmd.api.queries.GoogleDriveConnector.upload_file', return_value=({"alternateLink": "456"}))
    def test_create_gdrive_file(self, mock_upload, mock_get_session):
        organisation = {'name': 'UOB', 'gdrive_id': '456'}
        new_organisation = Organisation(**organisation)
        session.add(new_organisation)
        session.commit()
        organisation = session.query(Organisation).filter_by(name='UOB').first()
        user = {'organisation': organisation, 'username': '123', 'password': '123'}
        new_user = User(**user)
        session.add(new_user)
        session.commit()

        with app.test_client() as client:
            logged_in = client.post('/api/login', data=dumps({'username': '123', 'password': '123'}), headers=HEADERS)
            jwt = logged_in.json['access_token']
            data = {
                "partner": "UOB",
                "organism": "organism1",
                "exposure_conditions": [{"chemical_name": "chemical1", "doses": ["BDM10"], "timepoints": 1}],
                "exposure_batch": "AA",
                "replicate4control": 4,
                "replicate4exposure": 4,
                "replicate_blank": 2,
                "start_date": "2021-01-01",
                "end_date": "2022-01-01",
            }
            headers = {'Authorization': f'Bearer {jwt}', **HEADERS}
            response = client.post('/api/create_file', headers=headers, data=dumps(data))
            self.assertEqual(response.json["message"],
                             "ExposureCondition.dose must be one of ['0', 'BMD10', 'BMD25', '10mg/L'] but got BDM10")
            self.assertEqual(response.status_code, 400)

            data["exposure_conditions"][0]["doses"] = ["BMD10"]
            response = client.post('/api/create_file', headers=headers, data=dumps(data))
            self.assertEqual(response.json, {'data': {'file_url': '456'}})

