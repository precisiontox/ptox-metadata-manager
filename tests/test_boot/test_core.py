from unittest import TestCase
from unittest.mock import patch

from ptmd.boot import initialize


class MockUser:
    def __init__(self):
        self.username = 'user1'
        self.id = "123"
        self.name = 'UOX'
        self.gdrive_id = '1234'


@patch('ptmd.boot.core.Base')
@patch('ptmd.boot.core.User')
@patch('ptmd.boot.core.GoogleDriveConnector')
@patch('ptmd.boot.core.seed_db', return_value=({}, {}, {}, {}))
class TestInitializeApp(TestCase):

    def test_init_no_user(self, mock_boot, mock_gdc, mock_user, mock_base):
        mock_user.query.first.return_value = None
        initialize()
        mock_boot.assert_called_once()
        mock_base.metadata.create_all.assert_called_once()
        mock_gdc.assert_called_once()

    def test_init_with_users(self, mock_boot, mock_gdc, mock_user, mock_base):
        mock_user.query.first.return_value = MockUser()
        initialize()
        mock_boot.assert_not_called()
        mock_base.metadata.create_all.assert_called_once()
        mock_gdc.assert_called_once()
