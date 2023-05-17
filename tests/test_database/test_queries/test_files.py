from unittest import TestCase
from unittest.mock import patch

from ptmd.database.queries.files import create_files, prepare_files_data, extract_values_from_title

USER_ID = 1
ORGANISATION_NAME = 'JDHSKJFHDFHUERY_Aedes_aegypti_AA.xlsx'
DRIVE_ID = '1'
EXTRA_DATA = {'replicates': 1, 'controls': 1, 'blanks': 1, 'vehicle_name': 'DMSO'}
PREPARED_DATA = {
    'gdrive_id': DRIVE_ID,
    'name': ORGANISATION_NAME,
    'organisation_name': 'KIT',
    'user_id': USER_ID,
    'organism_name': 'Aedes_aegypti',
    'batch': 'AA',
    **EXTRA_DATA
}
DATA = {"KIT": [{'id': DRIVE_ID, 'title': ORGANISATION_NAME}], "CNR": None}


class TestFilesQueries(TestCase):

    def test_extract_values_from_title(self):
        title = 'WTTTFTFTFTFTFT_Aedes_aegypti_AA.xlsx'
        self.assertEqual(extract_values_from_title(title), ('Aedes_aegypti', 'AA'))

    @patch('ptmd.database.queries.files.User')
    @patch('ptmd.database.queries.files.Organisation')
    @patch('ptmd.database.queries.files.GoogleDriveConnector')
    @patch('ptmd.database.queries.files.remove')
    @patch('ptmd.database.queries.files.uuid4', return_value='uuid')
    @patch('ptmd.database.queries.files.extract_data_from_spreadsheet', return_value=EXTRA_DATA)
    def test_prepare_files_data(self, mock_extra_data, mock_uuid, mock_rm, mock_gdrive, mock_organisation, mock_user):
        mock_organisation.query.filter_by.return_value.first.return_value.name = 'KIT'
        mock_user.query.first.return_value.id = USER_ID
        mock_gdrive.return_value.download_file.return_value = 'path'

        prepared_files = prepare_files_data(DATA)
        self.assertEqual(prepared_files, [PREPARED_DATA])
        mock_rm.assert_called_once_with('path')
        expected_name = f"{ORGANISATION_NAME.replace('.xlsx', '_uuid.xlsx')}"
        mock_gdrive.return_value.download_file.assert_called_once_with(DRIVE_ID, expected_name)

    @patch('ptmd.database.queries.files.prepare_files_data', return_value=[PREPARED_DATA])
    @patch('ptmd.database.queries.files.session')
    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    def test_create_files(self, mock_chemical, mock_organism, mock_organisation, mock_session, mock_prepare_files_data):
        mock_organisation.query.filter_by.return_value.first.return_value.organisation_id = 1
        mock_organism.query.filter_by.return_value.first.return_value.organism_id = 1
        mock_chemical.query.filter_by.return_value.first.return_value.chemical_id = 1
        files = create_files(DATA)
        mock_prepare_files_data.assert_called_once_with(files_data=DATA)
        mock_session.add_all.assert_called_once()
        mock_session.commit.assert_called_once()
        file = files[0]
        self.assertEqual(file.gdrive_id, DRIVE_ID)
        self.assertEqual(file.name, ORGANISATION_NAME)
        self.assertEqual(file.organisation_id, 1)
        self.assertEqual(file.author_id, USER_ID)
        self.assertEqual(file.organism_id, 1)
        self.assertEqual(file.batch, 'AA')
