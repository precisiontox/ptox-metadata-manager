from unittest import TestCase
from unittest.mock import patch
from json import dumps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from flask_jwt_extended import create_access_token

from ptmd.database import Base, User
from ptmd.api import app


engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()
HEADERS = {'Content-Type': 'application/json'}


def create_user(username: str = '123'):
    user = {'organisation': None, 'username': username, 'password': '123'}
    new_user = User(**user)
    session.add(new_user)
    session.commit()
    return new_user


class MockedUser:
    def __init__(self, username):
        self.username = username


MOCKED_WORKING_USER = MockedUser(username='admin')
MOCKED_FAILING_USER = None


@patch('ptmd.api.queries.users.get_session', return_value=session)
@patch('ptmd.api.queries.utils.get_session', return_value=session)
class TestUser(TestCase):
    session: Session or None = None

    def setUp(self) -> None:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def test_login_failure(self, mock_get_session_1, mock_get_session_2):
        with app.test_client() as client:
            response = client.post('/api/login', data=dumps({}), headers=HEADERS)
            self.assertEqual(response.json, {"msg": "Missing username or password"})
            self.assertEqual(response.status_code, 400)

    @patch('ptmd.api.queries.users.login_user', return_value=({"access_token": "hello !"}, 200))
    def test_login_success(self, mock_login_user, mock_get_session_1, mock_get_session_2):
        pwd = "123"
        with app.test_client() as client:
            response = client.post('/api/login', headers=HEADERS,
                                   data=dumps({'username': '123', 'password': pwd}))
            self.assertEqual(response.json, mock_login_user.return_value[0])
            self.assertEqual(response.status_code, 200)

    def test_get_me(self, mock_get_session_1, mock_get_session_2):
        create_user()
        with app.test_client() as client:
            logged_in = client.post('/api/login', data=dumps({'username': '123', 'password': '123'}), headers=HEADERS)
            jwt = logged_in.json['access_token']
            response = client.get('/api/me', headers={'Authorization': f'Bearer {jwt}'})
            self.assertEqual(response.json, {'id': 1, 'organisation': None, 'username': '123'})
            self.assertEqual(response.status_code, 200)

            jwt = create_access_token(identity=2)
            response = client.get('/api/me', headers={'Authorization': f'Bearer {jwt}'})
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response.json, {'msg': 'Error loading the user 2'})

    def test_change_pwd(self, mock_get_session_1, mock_get_session_2):
        create_user()
        with app.test_client() as client:
            logged_in = client.post('/api/login', data=dumps({'username': '123', 'password': '123'}), headers=HEADERS)
            jwt = logged_in.json['access_token']
            HEADERS['Authorization'] = f'Bearer {jwt}'

            request = {
                "old_password": "123",
                "new_password": "1234",
                "confirm_password": "123"
            }
            response = client.post('/api/change_password', headers=HEADERS, data=dumps(request))
            self.assertEqual(response.json, {'msg': 'Passwords do not match'})
            self.assertEqual(response.status_code, 400)

            request["confirm_password"] = None
            response = client.post('/api/change_password', headers=HEADERS, data=dumps(request))
            self.assertEqual(response.json, {'msg': 'Missing new_password or confirm_password'})
            self.assertEqual(response.status_code, 400)

            request["confirm_password"] = "1234"
            request["old_password"] = "1234567"
            response = client.post('/api/change_password', headers=HEADERS, data=dumps(request))
            self.assertEqual(response.json, {'msg': 'Wrong password'})
            self.assertEqual(response.status_code, 400)

            request['old_password'] = "123"
            response = client.post('/api/change_password', headers=HEADERS, data=dumps(request))
            self.assertEqual(response.json, {'msg': 'Password changed successfully'})
            self.assertEqual(response.status_code, 200)

    @patch('ptmd.api.queries.utils.get_current_user', return_value=MOCKED_WORKING_USER)
    def test_create_user_success(self, mock_get_session_1, mock_get_session_2, mock_get_current_user):
        create_user(username='admin')
        with app.test_client() as client:
            response = client.post('/api/login', headers=HEADERS,
                                   data=dumps({'username': 'admin', 'password': '123'}))
            jwt = response.json['access_token']
            user_data = {
                "username": "1234",
                "password": "1234",
                "confirm_password": "1234",
                "organisation": "UOX"
            }
            created_user = client.post('/api/user', headers={'Authorization': f'Bearer {jwt}', **HEADERS},
                                       data=dumps(user_data))
            self.assertEqual(created_user.json, {'id': 2, 'organisation': None, 'username': '1234'})
            self.assertEqual(created_user.status_code, 200)

    @patch('ptmd.api.queries.utils.get_current_user', return_value=None)
    def test_create_user_unauthorized(self, mock_get_session_1, mock_get_session_2, mock_get_current_user):
        create_user(username='admin')
        with app.test_client() as client:
            response = client.post('/api/login', headers=HEADERS,
                                   data=dumps({'username': 'admin', 'password': '123'}))
            jwt = response.json['access_token']
            created_user = client.post('/api/user', headers={'Authorization': f'Bearer {jwt}', **HEADERS},
                                       data=dumps({}))
            self.assertEqual(created_user.json, {'msg': 'You are not authorized to create a new user'})
            self.assertEqual(created_user.status_code, 401)

    @patch('ptmd.api.queries.utils.get_current_user', return_value=MOCKED_WORKING_USER)
    def test_create_user_failures(self, mock_get_session_1, mock_get_session_2, mock_get_current_user):
        create_user(username='admin')
        with app.test_client() as client:
            response = client.post('/api/login', headers=HEADERS,
                                   data=dumps({'username': 'admin', 'password': '123'}))
            jwt = response.json['access_token']
            user_data = {
                "username": "1234",
                "password": "12345",
                "confirm_password": "1234",
                "organisation": "UOX"
            }
            created_user = client.post('/api/user', headers={'Authorization': f'Bearer {jwt}', **HEADERS},
                                       data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': "Passwords do not match"})
            self.assertEqual(created_user.status_code, 400)

            del user_data['password']
            created_user = client.post('/api/user', headers={'Authorization': f'Bearer {jwt}', **HEADERS},
                                       data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': "Missing password"})
            self.assertEqual(created_user.status_code, 400)

            user_data['password'] = "1234"
            user_data['username'] = "admin"
            created_user = client.post('/api/user', headers={'Authorization': f'Bearer {jwt}', **HEADERS},
                                       data=dumps(user_data))
            self.assertEqual(created_user.json, {'msg': "Username already taken"})
            self.assertEqual(created_user.status_code, 400)
