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

    @classmethod
    def setUpClass(cls) -> None:
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)()
        cls.session = session

        user_data = {'organisation': None, 'username': 'admin', 'password': 'admin'}
        user = User(**user_data)
        session.add(user)
        session.commit()

        with app.test_client() as client:
            response = client.post('/api/login', data=dumps({
                'username': 'admin',
                'password': 'admin'
            }), headers=HEADERS)
        cls.access_token = response.json['access_token']

    @classmethod
    def tearDownClass(cls) -> None:
        cls.session.close()

    @patch('ptmd.api.queries.validate.ExcelValidator', return_value=MockedValidator(1))
    def test_valid(self, mock_validator):
            with app.test_client() as client:
                headers = {'Authorization': f'Bearer {self.access_token}', **HEADERS}
                response = client.get('/api/file/1/validate', headers=headers)
            self.assertTrue(response.json['message'], "File validated successfully.")

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
