from unittest import TestCase
from unittest.mock import patch

from ptmd.database.models import Dose, Organism, Chemical, File


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


class TestDose(TestCase):

    def test_dose(self):
        dose_data = {
            "value": 1, "unit": "mg/L", "label": "BMD10",
            "organism": Organism(ptox_biosystem_name="A"),
            "chemical": Chemical(common_name="B")
        }
        dose = Dose(**dose_data)
        self.assertEqual(dict(dose), {
            'value': 1, 'unit': 'mg/L', 'label': 'BMD10', 'organism': 'A', 'chemical': 'B', 'files': []
        })

    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Chemical')
    def test_dose_with_file(self, mock_chemical, mock_file_organism, mock_file_organisation):
        mock_file_organisation.query.filter_by().first().organisation_id = 1
        mock_file_organism.query.filter_by().first().organism_id = 1
        mock_file_organism.query.filter_by().first().chemical_id = 1

        organism = Organism(ptox_biosystem_name="A")
        chemical = Chemical(common_name="B")
        file = File(**DATA)
        dose = Dose(value=1, unit='mg/kg', label="BMD10", organism=organism, chemical=chemical, files=[file])
        self.assertEqual(dict(dose.files[0]), {
            'author': None,
            'batch': 'AA',
            'doses': [{'label': 'BMD10', 'unit': 'mg/kg', 'value': 1}],
            'file_id': None,
            'gdrive_id': '123',
            'name': 'test',
            'organisation': None,
            'organism': None,
            'replicates': 1,
            'controls': 1,
            'blanks': 1,
            'vehicle': None,
            'chemicals': [],
            'timepoints': [],
            'validated': None,
            'received': None,
            'shipped': None
        })
