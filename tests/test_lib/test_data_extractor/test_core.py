from unittest import TestCase
from unittest.mock import patch
from uuid import uuid4

from ptmd.lib.data_extractor.core import extract_data_from_spreadsheet


class TestDataExtractor(TestCase):

    @patch('ptmd.lib.data_extractor.core.ExcelFile')
    def test_extraction_valid(self, mock_excel):
        mock_excel.return_value.parse.return_value.to_dict.return_value = [{
            'replicates': 3,
            'control': 1,
            'blanks': 1,
            'compound_vehicle': 'DMSO'
        }]
        data = extract_data_from_spreadsheet('test.xlsx')
        self.assertEqual(data, {
            'replicates': 3,
            'controls': 1,
            'blanks': 1,
            'vehicle_name': 'DMSO'
        })

    def test_extraction_invalid(self):
        data = extract_data_from_spreadsheet(f'{uuid4()}.xlsx')
        self.assertEqual(data, None)
