from unittest import TestCase
from unittest.mock import patch, mock_open

from ptmd.database import File


@patch("builtins.open", mock_open(read_data="{'save_credentials_file': 'test'}"))
class TestFile(TestCase):

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    def test_files(self, mock_organism, mock_organisation):
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        file = File(**{
            'gdrive_id': '123',
            'name': 'test',
            'batch': 'AA',
            'organisation_name': None,
            'user_id': None,
            'organism_name': None})
        self.assertEqual(dict(file), {
            'file_id': None,
            'gdrive_id': '123',
            'name': 'test',
            'batch': 'AA',
            'organisation': None,
            'author': None,
            'organism': None,
        })
