from unittest import TestCase
from unittest.mock import patch
from copy import deepcopy
from os import path

from jsonschema import ValidationError

from ptmd.lib.creator.core import DataframeCreator
from ptmd.const import ALLOWED_PARTNERS


HERE = path.abspath(path.dirname(__file__))


VALID_INPUT = {
    "partner": ALLOWED_PARTNERS[0],
    "organism": "H",
    "exposure_batch": "AC",
    "replicates4exposure": 2,
    "replicates4control": 2,
    "replicates_blank": 1,
    "exposure": [{}],
    "start_date": "2020-01-01",
    "end_date": "2020-01-01",
    "vehicle": "Water",
    "timepoints": [1, 2, 3]

}
CHEMICAL_MAPPING: dict = {
    "chemical1": "001",
    "chemical2": "002",
    "chemical3": "003"
}


class TestFileCreator(TestCase):

    def test_error_partner(self):
        data: dict = {'start_date': '2020-01-01', 'end_date': '2020-01-01', 'timepoints': [1, 2, 3]}
        with self.assertRaises(ValidationError) as context:
            DataframeCreator(data)
        self.assertEqual("'partner' is a required property", str(context.exception))

        data["partner"] = "ABC"
        with self.assertRaises(ValidationError) as context:
            DataframeCreator(data)
        self.assertEqual(f"'partner' value 'ABC' is not one of {ALLOWED_PARTNERS}",
                         str(context.exception))

        data["partner"] = 1
        with self.assertRaises(ValidationError) as context:
            DataframeCreator(data)
        self.assertEqual("'partner' value 1 is not of type 'string'",
                         str(context.exception))

    def test_error_missing_exposure(self):
        data = VALID_INPUT
        with self.assertRaises(ValidationError) as context:
            DataframeCreator(data)
            DataframeCreator(data)
        self.assertEqual("'exposure' value 'chemicals' is a required property",
                         str(context.exception))

    @patch('ptmd.lib.creator.core.get_chemical_code_mapping', return_value=CHEMICAL_MAPPING)
    @patch('ptmd.lib.creator.core.get_organism_code', return_value='H')
    @patch('ptmd.lib.creator.core.get_allowed_organisms', return_value=['H'])
    def test_success(self, mock_chemical_mapping, mock_organism_code, mock_allowed_organisms):
        data = deepcopy(VALID_INPUT)
        data['exposure'] = [{"chemicals": ["chemical1", "chemical1", "chemical2"], "dose": 0}]
        creator: DataframeCreator = DataframeCreator(data)
        df1, df2 = creator.to_dataframe()
        self.assertEqual(df1.shape, (25, 19))
        self.assertEqual(df2.shape, (1, 10))

        output_path = path.join(HERE, "..", "..", "test.xlsx")
        file_path = creator.save_file(output_path)
        self.assertIsNotNone(file_path)
        creator.delete_file()

    @patch('ptmd.lib.creator.core.get_chemical_code_mapping', return_value=CHEMICAL_MAPPING)
    @patch('ptmd.lib.creator.core.get_organism_code', return_value='H')
    @patch('ptmd.lib.creator.core.get_allowed_organisms', return_value=['H'])
    def test_cannot_delete_file(self, mock_chemical_mapping, mock_organism_code, mock_allowed_organisms):
        data = deepcopy(VALID_INPUT)
        data['exposure'] = [{"chemicals": ["chemical1", "chemical1", "chemical2"], "dose": 0}]
        creator: DataframeCreator = DataframeCreator(data)
        with self.assertRaises(FileNotFoundError) as context:
            creator.delete_file()
        self.assertEqual("This input was not saved yet.", str(context.exception))

    @patch('ptmd.lib.creator.core.get_allowed_organisms', return_value=['W'])
    def test_missing_organism(self, mock_allowed_organisms):
        data = deepcopy(VALID_INPUT)
        data['exposure'] = [{"chemicals": ["chemical1", "chemical1", "chemical2"], "dose": 0}]
        creator: DataframeCreator = DataframeCreator(data)
        with self.assertRaises(ValueError) as context:
            creator.to_dataframe()
        self.assertEqual("Organism H not found in the database.", str(context.exception))

    @patch('ptmd.lib.creator.core.get_chemical_code_mapping', return_value=CHEMICAL_MAPPING)
    @patch('ptmd.lib.creator.core.get_organism_code', return_value='H')
    @patch('ptmd.lib.creator.core.get_allowed_organisms', return_value=['H'])
    def test_overextending_timeframe(self, mock_chemical_mapping, mock_organism_code, mock_allowed_organisms):
        data = deepcopy(VALID_INPUT)
        data['exposure'] = [{"chemicals": ["chemical1", "chemical1", "chemical2"], "dose": 0}]
        data['start_date'] = '2020-01-01'
        data['end_date'] = '2020-01-01'
        data['timepoints'] = [1, 2, 30000000]
        with self.assertRaises(ValidationError) as context:
            creator: DataframeCreator = DataframeCreator(data)
            creator.validate()
        self.assertEqual(str(context.exception), "Timepoint 30000000 is over extending the end date.")

