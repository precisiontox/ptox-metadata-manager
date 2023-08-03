from unittest import TestCase
from unittest.mock import patch

from ptmd.lib.validator.validate_identifier import (
    validate_identifier,
    validate_species,
    validate_batch,
    validate_compound,
    validate_dose,
    validate_timepoints,
    validate_replicate,
)
from ptmd.lib.validator.const import PTX_ID_LABEL, COMPOUND_LABEL, DOSE_LABEL, TIMEPOINT_LABEL


class ExcelValidatorMock:

    def __init__(self):
        self.report: dict = {'valid': True, 'errors': {}}
        self.current_record: dict = {
            'data': {
                PTX_ID_LABEL: 'FAC002LA1',
                "compound_name": "Compound 1",
                "dose_code": "BMD10",
                "timepoint_level": "TP1",
                "replicate": 1
            },
            'label': 'test'
        }
        self.general_info: dict = {
            'exposure_batch': 'AC',
            'biosystem_name': 'test',
            'dose_code': 'BMD10',
            'compound_name': 'Compound 1',
        }
        self.exposure_data: list[dict] = []
        self.identifiers: list[str] = []

    def add_error(self, label, message, field):
        self.report['valid'] = False
        if label not in self.report['errors']:
            self.report['errors'][label] = []
        self.report['errors'][label].append({'message': message, 'field_concerned': field})


class TestValidateIdentifier(TestCase):

    def test_validate_identifier_failure(self):
        validator = ExcelValidatorMock()
        validator.identifiers = ['FAC002LA1', 'PTX002']
        validate_identifier(validator, 0)
        self.assertFalse(validator.report['valid'])
        expected_error = {
            'message': 'Record at line 2 (FAC002LA1) is duplicated with record at line 3',
            'field_concerned': 'precisionTox_short_identifier'
        }
        self.assertEqual(validator.report['errors']['test'][0], expected_error)

    @patch('ptmd.lib.validator.validate_identifier.Organism')
    @patch('ptmd.lib.validator.validate_identifier.Chemical')
    def test_validate_identifier_success(self, mock_chemical, mock_organisms):
        mock_chemical.query.filter().first.return_value.ptx_code = 2
        mock_organisms.query.filter().first.return_value.ptox_biosystem_code = 'F'
        validator = ExcelValidatorMock()
        validator.identifiers = []
        validate_identifier(validator, 1)
        self.assertTrue(validator.report['valid'])

    @patch('ptmd.lib.validator.validate_identifier.Organism')
    def test_validate_species_error_404(self, mock_organisms):
        mock_organisms.query.filter().first.return_value = None
        validator = ExcelValidatorMock()
        validate_species(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'], 'Organism not found in database.')

    @patch('ptmd.lib.validator.validate_identifier.Organism')
    def test_validate_species_error_unmatch(self, mock_organisms):
        mock_organisms.query.filter().first.return_value.ptox_biosystem_code = 'ABCF'
        validator = ExcelValidatorMock()
        validator.general_info['biosystem_name'] = 'test2'
        validate_species(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier organism doesn't match the biosystem_name.")

    def test_validate_species_error_unknown(self):
        validator = ExcelValidatorMock()
        validator.general_info['biosystem_name'] = 'test2'
        validate_species(validator)
        self.assertFalse(validator.report['valid'])
        self.assertIn("Error Working outside of application context.", validator.report['errors']['test'][0]['message'])

    def test_validate_batch_error_wrong_batch_general_info(self):
        validator = ExcelValidatorMock()
        validator.general_info['exposure_batch'] = 'ABC'
        validate_batch(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'], "The batch 'ABC' is not valid.")
        self.assertEqual(validator.report['errors']['test'][0]['field_concerned'], 'exposure_batch')

    def test_validate_batch_error_wrong_batch_identifier(self):
        validator = ExcelValidatorMock()
        validator.current_record['data'][PTX_ID_LABEL] = 'Fq^002LA1'
        validate_batch(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier doesn't contain a valid batch 'q^'.")
        self.assertEqual(validator.report['errors']['test'][0]['field_concerned'], PTX_ID_LABEL)

    def test_validate_batch_error_unmatch(self):
        validator = ExcelValidatorMock()
        validator.current_record['data'][PTX_ID_LABEL] = 'FBC002LA1'
        validate_batch(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier batch doesn't match the batch 'AC'.")
        self.assertEqual(validator.report['errors']['test'][0]['field_concerned'], PTX_ID_LABEL)

    def test_validate_compound_error_too_low(self):
        validator = ExcelValidatorMock()
        validator.current_record['data'][PTX_ID_LABEL] = 'FBC-01LA1'
        validate_compound(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier doesn't contain a valid compound code '-1'.")

    @patch('ptmd.lib.validator.validate_identifier.Chemical')
    def test_validate_compound_replicates(self, mock_chemical):
        mock_chemical.query.filter().first.return_value.ptx_code = '2'
        validator = ExcelValidatorMock()
        validator.current_record['data'][PTX_ID_LABEL] = 'FBC003LA1'
        validate_compound(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier 3 compound doesn't match the compound Compound 1 (2)")

    def test_validate_compound_replicates_error_unknown(self):
        validator = ExcelValidatorMock()
        validator.current_record['data'][PTX_ID_LABEL] = 'FBC003LA1'
        validate_compound(validator)
        self.assertFalse(validator.report['valid'])
        self.assertIn("Error Working outside of application context.", validator.report['errors']['test'][0]['message'])

    @patch('ptmd.lib.validator.validate_identifier.Chemical')
    def test_validate_compound_error_no_compound(self, mock_chemical):
        mock_chemical.query.filter().first.return_value = None
        validator = ExcelValidatorMock()
        validator.current_record['data'][PTX_ID_LABEL] = 'FBC003LA1'
        validate_compound(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier doesn't contain a valid compound code '3'.")

    @patch('ptmd.lib.validator.validate_identifier.Chemical')
    def test_validate_compound_controls(self, mock_chemical):
        mock_chemical.query.filter().first.return_value.ptx_code = '2'
        validator = ExcelValidatorMock()
        validator.current_record['data'][COMPOUND_LABEL] = 'CONTROL (DMSO)'
        validate_compound(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier compound should be 999 but got 2.")

        validator = ExcelValidatorMock()
        validator.current_record['data'][COMPOUND_LABEL] = 'CONTROL (WATER)'
        validate_compound(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier compound should be 997 but got 2.")

    def test_validate_compound_blanks(self):
        validator = ExcelValidatorMock()
        validator.current_record['data'][COMPOUND_LABEL] = 'EXTRACTION BLANK'
        validate_compound(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier compound should be 998 but got 2.")

    def test_validate_dose(self):
        validator = ExcelValidatorMock()
        validator.current_record['data'][DOSE_LABEL] = 'BMD25'

        validate_dose(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier dose maps to BMD10 but should maps to 'BMD25'.")

        validator = ExcelValidatorMock()
        validator.current_record['data'][PTX_ID_LABEL] = 'FAC002WA1'
        validate_dose(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'], "The identifier contain a invalid dose 'W'.")

    def test_validate_timepoints(self):
        validator = ExcelValidatorMock()
        validator.current_record['data'][TIMEPOINT_LABEL] = 'TP0'
        validate_timepoints(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier timepoints maps to TP1 but should maps to 'TP0'.")

        validator = ExcelValidatorMock()
        validator.current_record['data'][PTX_ID_LABEL] = 'FAC002LW1'
        validate_timepoints(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier contains an invalid timepoint 'W'.")

    def test_validate_replicate(self):
        validator = ExcelValidatorMock()
        validator.current_record['data'][PTX_ID_LABEL] = 'FAC002LA19'
        validate_replicate(validator)
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['test'][0]['message'],
                         "The identifier replicate 9 doesn't match the replicate 1.")
