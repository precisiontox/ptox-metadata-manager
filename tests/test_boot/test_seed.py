from unittest import TestCase
from unittest.mock import patch

from ptmd.boot.seed import seed_db

mock_empty_data: dict = {
    'organisations': [],
    'users': [],
    'chemicals': [],
    'organisms': []
}


class TestBootCore(TestCase):

    def setUp(self) -> None:
        self.input_orgs = {'KIT': {"g_drive": "123", "long_name": "test12"}}

    @patch('ptmd.boot.seed.create_organisations', return_value={'UOX': 1})
    @patch('ptmd.boot.seed.create_users', return_value={'test': 1})
    @patch('ptmd.boot.seed.create_chemicals', return_value={'test': 1})
    @patch('ptmd.boot.seed.create_organisms', return_value={'test': 1})
    def test_seed(self, mock_organisms, mock_chemicals, mocked_create_users, mock_create_organisations):
        organisations, users, chemicals, organisms = seed_db(**mock_empty_data)
        mocked_create_users.assert_called()
        mock_create_organisations.assert_called()
        self.assertEqual(organisations, mock_create_organisations.return_value)
        self.assertEqual(users, mocked_create_users.return_value)
        self.assertEqual(chemicals, mock_chemicals.return_value)
        self.assertEqual(organisms, mock_organisms.return_value)
