from unittest import TestCase
from unittest.mock import patch

from ptmd.boot.seed import seed_db

mock_empty_data: dict = {
    'organisations': [],
    'users': [],
    'chemicals': [],
    'organisms': [],
    'files': {}
}


class TestBootCore(TestCase):

    def setUp(self) -> None:
        self.input_orgs = {'KIT': {"g_drive": "123", "long_name": "test12"}}

    @patch('ptmd.boot.seed.create_files', return_value={'test': 1})
    @patch('ptmd.boot.seed.create_organisations', return_value={'UOX': 1})
    @patch('ptmd.boot.seed.create_users', return_value={'test': 1})
    @patch('ptmd.boot.seed.create_chemicals', return_value={'test': 1})
    @patch('ptmd.boot.seed.create_organisms', return_value={'test': 1})
    def test_seed(self, mock_organisms, mock_chemicals, mock_users, mock_organisations, mock_files):
        organisations, users, chemicals, organisms, files = seed_db(**mock_empty_data)
        mock_users.assert_called()
        mock_organisations.assert_called()
        self.assertEqual(organisations, mock_organisations.return_value)
        self.assertEqual(users, mock_users.return_value)
        self.assertEqual(chemicals, mock_chemicals.return_value)
        self.assertEqual(organisms, mock_organisms.return_value)
