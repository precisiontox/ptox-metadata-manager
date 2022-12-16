from unittest import TestCase
from unittest.mock import patch

from sqlalchemy.orm import Session

from ptmd.const import CONFIG
from ptmd.utils import get_session, init


class TestAPIUtilities(TestCase):

    @patch('ptmd.utils.initialize')
    @patch('ptmd.utils.get_session', return_value=Session())
    def test_init(self, mock_get_session, mock_init):
        init()
        mock_init.assert_called_once()
        mock_init.assert_called_with(users=[{'username': 'admin', 'password': 'admin', 'organisation': 'UOX'}],
                                     session=mock_get_session.return_value)

    @patch('ptmd.database.Base.metadata.create_all', return_value=None)
    @patch('ptmd.database.utils.create_engine', return_value="abc")
    def test_get_session(self, mock_create_engine, mock_create_all):
        session = get_session()
        self.assertIsInstance(session, Session)
        mock_create_engine.assert_called_once()
        mock_create_engine.assert_called_with(CONFIG['SQLALCHEMY_DATABASE_URL'])
