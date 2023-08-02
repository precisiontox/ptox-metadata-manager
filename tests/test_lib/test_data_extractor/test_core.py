from unittest import TestCase
from unittest.mock import patch

from ptmd.lib.data_extractor.core import extract_data_from_spreadsheet


class TestDataExtractor(TestCase):

    @patch('ptmd.lib.data_extractor.core.ExcelFile')
    @patch('ptmd.lib.data_extractor.core.get_chemicals_from_name', return_value=["a", "b", "c"])
    @patch('ptmd.lib.data_extractor.core.create_timepoints_hours', return_value=[1, 2, 3])
    def test_extraction_valid(self, mock_tp, mock_chemicals, mock_excel):
        mock_excel.return_value.parse.return_value.to_dict.return_value = [{
            'replicates': 3,
            'control': 1,
            'blanks': 1,
            'compound_vehicle': 'DMSO',
            'timepoints': "[1, 2, 3]",
            'biosystem_name': 'H',
            'exposure_batch': "AA",
            'partner_id': "UOX",
            'exposure_batch_startdate': "2021-01-01",
            'exposure_batch_enddate': "2021-01-01"
        }]
        data = extract_data_from_spreadsheet('test.xlsx')
        self.assertEqual(data, {
            'replicates': 3,
            'controls': 1,
            'blanks': 1,
            'vehicle_name': 'DMSO',
            'chemicals': ['a', 'b', 'c'],
            'timepoints': [1, 2, 3],
            'batch': 'AA',
            'organisation_name': 'UOX',
            'organism_name': 'H',
            'start_date': '2021-01-01',
            'end_date': '2021-01-01'
        })
        mock_chemicals.assert_called_once()
        mock_tp.assert_called_once()
