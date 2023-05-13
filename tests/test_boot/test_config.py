from os import path
from unittest import TestCase
from unittest.mock import patch, mock_open

from ptmd.boot import create_config_file


@patch('ptmd.boot.config.exists', return_value=False)
@patch('ptmd.boot.config.dump', return_value=True)
class TestCreateConfigFile(TestCase):

    def setUp(self):
        self.mock_path = path.join(path.dirname(path.abspath(__file__)), 'data', 'test_config.yaml')
        self.mock_settings = patch('ptmd.boot.config.GOOGLE_DRIVE_SETTINGS_FILE_PATH', self.mock_path)

    def test_create_config_file(self, mock_dump, mock_exists):
        with self.mock_settings:
            with patch("builtins.open", mock_open(read_data="data")):
                gdrive_settings = create_config_file()
                mock_exists.assert_called_once()
                mock_dump.assert_called_once()
                self.assertIsNotNone(gdrive_settings)
