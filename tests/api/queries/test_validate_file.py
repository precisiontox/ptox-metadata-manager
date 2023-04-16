from unittest import TestCase
from unittest.mock import patch
from json import dumps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ptmd.database import Base, User
from ptmd.api import app
from ptmd.api.queries.validate import validate_file


HEADERS = {'Content-Type': 'application/json'}


class MockedValidator:
    def __init__(self, file_id):
        self.report = {'valid': True, 'errors': []}


class MockedValidatorError:
    def __init__(self, file_id):
        self.report = {'valid': False, 'errors': ['error']}


class TestValidateFile(TestCase):

    @patch('ptmd.api.queries.validate.ExcelValidator', return_value=MockedValidator(1))
    def test_valid(self, mock_validator):
        report, code = validate_file(1)
        self.assertTrue(report['message'], "File validated successfully.")

    @patch('ptmd.api.queries.validate.ExcelValidator', return_value=MockedValidatorError(1))
    def test_error_400(self, mock_validator):
        report, code = validate_file(1)
        self.assertEqual(report['message'], 'File validation failed.')
        self.assertEqual(code, 400)

        report, code = validate_file('a')
        self.assertEqual(report['error'], 'File ID must be an integer.')
        self.assertEqual(code, 400)

    def test_error_404(self):
        report, code = validate_file(10)
        self.assertEqual(report['error'], 'File with ID 10 does not exist.')
        self.assertEqual(code, 404)

    @patch('ptmd.api.routes.validate_file', return_value=({'message': 'File validated successfully.'}, 200))
    def test_route(self, mock_validate):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        session = session

        user_data = {'organisation': None, 'username': 'admin', 'password': 'admin'}
        user = User(**user_data)
        session.add(user)
        session.commit()

        with app.test_client() as client:
            response = client.post('/api/login', data=dumps({
                'username': 'admin',
                'password': 'admin'
            }), headers=HEADERS)
        print(response.json)
        access_token = response.json['access_token']

        with app.test_client() as client:
            response = client.get('/api/file/1/validate',
                                  headers={'Authorization': f'Bearer {access_token}', **HEADERS})
        print(response.json)
