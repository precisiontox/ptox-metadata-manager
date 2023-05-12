from unittest import TestCase
from unittest.mock import patch

from ptmd.database import create_organisations


INPUTS_ORGS = {'KIT': {"g_drive": "123", "long_name": "test12"}}


class TestOrganisationsQueries(TestCase):

    @patch('ptmd.database.queries.organisations.session')
    @patch('ptmd.database.queries.organisations.Organisation')
    def test_create_organisations(self, mock_organisation, mock_session):
        mock_organisation.query.filter().first.return_value = INPUTS_ORGS['KIT']
        organisations = create_organisations(organisations=INPUTS_ORGS)
        self.assertTrue(mock_session.commit.called)
        self.assertTrue(mock_session.add)
        organisations = {org: dict(organisations[org]) for org in organisations}
        self.assertEqual(organisations['KIT']['g_drive'], "123")
