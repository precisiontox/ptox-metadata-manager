from unittest import TestCase
from unittest.mock import patch, mock_open

from ptmd.database import File, Dose, Timepoint


DATA = {
    'gdrive_id': '123',
    'name': 'test',
    'organisation_name': 'test',
    'user_id': 1,
    'organism_name': 'test',
    'batch': 'AA',
    'replicates': 1,
    'controls': 1,
    'blanks': 1,
    'vehicle_name': 'test'
}


@patch("builtins.open", mock_open(read_data="{'save_credentials_file': 'test'}"))
class TestFile(TestCase):

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    def test_files(self, mock_chemical, mock_organism, mock_organisation):
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        mock_chemical.query.filter_by().first().chemical_id = 1
        file = File(**DATA)
        self.assertEqual(dict(file), {
            'file_id': None,
            'gdrive_id': '123',
            'name': 'test',
            'batch': 'AA',
            'replicates': 1,
            'controls': 1,
            'blanks': 1,
            'organisation': None,
            'author': None,
            'organism': None,
            'vehicle': None,
            'doses': [],
            'chemicals': [],
            'timepoints': [],
            'validated': None,
            'shipped': None,
            'received': None
        })

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    def test_file_with_dose_and_timepoints(self, mock_chemical, mock_organism, mock_organisation):
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        mock_chemical.query.filter_by().first().chemical_id = 1
        dose = Dose(value=1, unit='mg/kg', label="BMD10", organism_id=1, chemical_id=1)
        file = File(**DATA, doses=[dose])
        self.assertEqual(dict(file)['doses'], [{'value': 1, 'unit': 'mg/kg', 'label': 'BMD10'}])
        self.assertEqual(file.doses[0].organism_id, 1)
        self.assertEqual(file.doses[0].chemical_id, 1)

        timepoint = Timepoint(value=1, unit='mg/kg', label="BMD10")
        file = File(**DATA, timepoints=[timepoint])
        self.assertEqual(dict(file)['timepoints'][0], {'files': ['123'], 'label': 'BMD10', 'unit': 'mg/kg', 'value': 1})

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.get_current_user')
    @patch('ptmd.database.models.file.session')
    def test_remove_file_permission_denied(self, mock_session, mock_user, mock_chemical,
                                           mock_organism, mock_organisation):
        mock_user.return_value.role = 'NONE'
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        mock_chemical.query.filter_by().first().chemical_id = 1
        file = File(**DATA)
        with self.assertRaises(PermissionError) as context:
            file.remove()
        self.assertEqual(str(context.exception), "You don't have permission to delete file None.")

        with patch('ptmd.database.models.file.GoogleDriveConnector') as mock_drive:
            mock_user.return_value.role = 'admin'
            mock_drive.return_value.delete_file.side_effect = PermissionError()
            file.remove()
            mock_session.delete.assert_called_once_with(file)
            mock_session.commit.assert_called_once()

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.get_current_user')
    @patch('ptmd.database.models.file.GoogleDriveConnector')
    @patch('ptmd.database.models.file.session')
    def test_remove_file_success(self, mock_session, mock_gdrive,
                                 mock_user, mock_chemical, mock_organism, mock_organisation):
        mock_user.return_value.role = 'admin'
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        mock_chemical.query.filter_by().first().chemical_id = 1
        file = File(**DATA)
        file.remove()
        mock_gdrive.return_value.delete_file.assert_called_once_with(file.gdrive_id)
        mock_session.delete.assert_called_once_with(file)
        mock_session.commit.assert_called_once()

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.get_current_user')
    def test_receive_shipment_error_permission_denied(self, mock_user, mock_chemical, mock_organism, mock_organisation):
        mock_user.return_value.role = 'NONE'
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        mock_chemical.query.filter_by().first().chemical_id = 1
        file = File(**DATA)
        with self.assertRaises(PermissionError) as context:
            file.shipment_was_received()
        self.assertEqual(str(context.exception),
                         "You don't have permission to update to receive shipment for file None.")

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.get_current_user')
    def test_receive_shipment_error_not_shipped(self, mock_user, mock_chemical, mock_organism, mock_organisation):
        mock_user.return_value.role = 'admin'
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        mock_chemical.query.filter_by().first().chemical_id = 1
        file = File(**DATA)
        with self.assertRaises(ValueError) as context:
            file.shipment_was_received()
        self.assertEqual(str(context.exception), "File None has not been shipped yet.")

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.get_current_user')
    @patch('ptmd.database.models.file.session')
    def test_receive_shipment_success(self, mock_session, mock_user, mock_chemical, mock_organism, mock_organisation):
        mock_user.return_value.role = 'admin'
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        mock_chemical.query.filter_by().first().chemical_id = 1
        file = File(**DATA)
        file.shipped = True
        file.shipment_was_received()
        self.assertTrue(file.received)
        mock_session.commit.assert_called_once()

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.get_current_user')
    def test_ship_sample_error_permission_denied(self, mock_user, mock_chemical, mock_organism, mock_organisation):
        mock_user.return_value.role = 'None'
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        mock_chemical.query.filter_by().first().chemical_id = 1
        file = File(**DATA)
        with self.assertRaises(PermissionError) as context:
            file.ship_samples()
        self.assertEqual(str(context.exception), "You don't have permission to ship file None.")

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.get_current_user')
    def test_ship_sample_error_not_valid_file(self, mock_user, mock_chemical, mock_organism, mock_organisation):
        mock_user.return_value.role = 'admin'
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        mock_chemical.query.filter_by().first().chemical_id = 1
        file = File(**DATA)
        file.validated = 'invalid'
        with self.assertRaises(ValueError) as context:
            file.ship_samples()
        self.assertEqual(str(context.exception), "File None has not been validated yet or has failed validation.")

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.get_current_user')
    def test_ship_sample_error_already_shipped(self, mock_user, mock_chemical, mock_organism, mock_organisation):
        mock_user.return_value.role = 'admin'
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        mock_chemical.query.filter_by().first().chemical_id = 1
        file = File(**DATA)
        file.validated = 'success'
        file.shipped = True
        with self.assertRaises(ValueError) as context:
            file.ship_samples()
        self.assertEqual(str(context.exception), "File None has already been shipped.")

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.get_current_user')
    @patch('ptmd.database.models.file.session')
    def test_ship_samples_success(self, mock_session, mock_user, mock_chemical, mock_organism, mock_organisation):
        mock_user.return_value.role = 'admin'
        mock_organisation.query.filter_by().first().organisation_id = 1
        mock_organism.query.filter_by().first().organism_id = 1
        mock_chemical.query.filter_by().first().chemical_id = 1
        file = File(**DATA)
        file.validated = 'success'
        file.ship_samples()
        self.assertTrue(file.shipped)
        mock_session.commit.assert_called_once()
