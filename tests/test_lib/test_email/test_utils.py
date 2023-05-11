from unittest import TestCase
from unittest.mock import patch, mock_open

from ptmd.lib.email.utils import get_config


class TestUtilities(TestCase):

    @patch('builtins.open', mock_open(read_data="{'save_credentials_file': 'data'}"))
    def test_get_config(self):
        self.assertEqual(get_config(), 'data')