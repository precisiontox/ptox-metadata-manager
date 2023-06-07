from unittest import TestCase
from unittest.mock import patch, mock_open

from ptmd.database import Organisation


@patch("builtins.open", mock_open(read_data="{'save_credentials_file': 'test'}"))
class TestOrganisation(TestCase):

    def test_organisation_no_user(self):
        expected_organisation: dict = {'name': 'UOX', 'longname': None}
        with patch('ptmd.database.models.organisation.get_current_user') as mock_get_current_user:
            mock_get_current_user.return_value = None
            organisation = Organisation(name=expected_organisation['name'], gdrive_id=None)
            self.assertEqual(dict(organisation), expected_organisation)

    def test_organisation_admin(self):
        expected_organisation: dict = {
            'files': [],
            'gdrive_id': None,
            'longname': None,
            'name': 'UOX',
            'organisation_id': None
        }
        with patch('ptmd.database.models.organisation.get_current_user') as mock_get_current_user:
            mock_get_current_user.return_value.role = 'admin'
            organisation = Organisation(name=expected_organisation['name'], gdrive_id=None)
            self.assertEqual(dict(organisation), expected_organisation)
