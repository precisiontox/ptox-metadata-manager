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
            'timepoints': []
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
