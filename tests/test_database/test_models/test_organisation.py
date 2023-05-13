from unittest import TestCase
from unittest.mock import patch, mock_open

from ptmd.database import Organisation


@patch("builtins.open", mock_open(read_data="{'save_credentials_file': 'test'}"))
class TestOrganisation(TestCase):

    def test_organisation(self):
        expected_organisation = {
            'name': 'UOX', 'organisation_id': None, 'gdrive_id': 'test', 'longname': None, 'files': []
        }
        organisation = Organisation(name=expected_organisation['name'], gdrive_id=expected_organisation['gdrive_id'])
        self.assertEqual(dict(organisation), expected_organisation)
