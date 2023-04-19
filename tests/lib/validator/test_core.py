from unittest import TestCase
from unittest.mock import patch
from copy import deepcopy

from pandas import DataFrame, Series, concat

from ptmd.lib.validator.core import ExcelValidator, ExternalExcelValidator, VerticalValidator
from ptmd.const import SAMPLE_SHEET_COLUMNS, GENERAL_SHEET_COLUMNS


class MockGoogleDriveAPI:
    def __init__(self, *args, **kwargs):
        pass

    def CreateFile(self, *args, **kwargs):
        return {"title": "test.xlxs"}


class MockSession:
    def __init__(self, *args, **kwargs):
        self.ptox_biosystem_code = 'F'
        self.ptx_code = 'PTX001'

    def query(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def first(self, *args, **kwargs):
        return self

    def close(self):
        pass

    def __iter__(self):
        mock = {'gdrive_id': '1', 'name': 'test.xlsx', 'file_id': 1}
        for k, v in mock.items():
            yield k, v

    def update(self, *args, **kwargs):
        pass

    def commit(self):
        pass


class MockSessionError(MockSession):
    def first(self, *args, **kwargs):
        return None


class MockGoogleDriveConnector:
    def __init__(self, *args, **kwargs):
        self.google_drive = MockGoogleDriveAPI()

    def download_file(self, *args, **kwargs):
        return 'PTX001.xlsx'


mocked_session = MockSession()
mocked_session_error = MockSessionError()
mock_exposure_dataframe = DataFrame(columns=SAMPLE_SHEET_COLUMNS)
mock_exposure_series = Series([
    "qsd", "qsd", "qsd", "qsd", "qsd", "qsd", 12, 12, 1, "A", 1, None, None, None,
    1, "Ethoprophos", "BMD10", "TP1", 4, "FAC002LA1"
], index=SAMPLE_SHEET_COLUMNS)
mock_exposure_dataframe = concat([mock_exposure_dataframe, mock_exposure_series.to_frame().T],
                                 ignore_index=False, sort=False, copy=False)
mock_exposure_series_error = Series([
    "qsd", "qsd", "qsd", "qsd", None, "qsd", 12, 12, 1, "A", 1, None, None, None,
    1, "Ethoprophos", "BMD10", "TP1", 4, "FAC002LA1"
], index=SAMPLE_SHEET_COLUMNS)
mock_exposure_dataframe_error = concat([mock_exposure_dataframe, mock_exposure_series_error.to_frame().T],
                                       ignore_index=False, sort=False, copy=False)

mock_general_dataframe = DataFrame(columns=GENERAL_SHEET_COLUMNS)
mock_general_series = Series(
    ["UOB", "Drosophila_melanogaster_female", "AC", 1, 1, 0, "2020-01-01", "2020-10-01", "[4]", "DMSO"],
    index=GENERAL_SHEET_COLUMNS
)
mock_general_dataframe = concat([mock_general_dataframe, mock_general_series.to_frame().T],
                                ignore_index=False, sort=False, copy=False)


class MockExcelFileSuccess:
    def __init__(self, *args, **kwargs):
        pass

    def parse(self, sheet_name, *args, **kwargs):
        if sheet_name == "General Information":
            return mock_general_dataframe
        elif sheet_name == "Exposure information":
            return mock_exposure_dataframe

    def validate(self, *args, **kwargs):
        pass


class MockExcelFileError:
    def __init__(self, *args, **kwargs):
        pass

    def parse(self, sheet_name, *args, **kwargs):
        if sheet_name == "General Information":
            return mock_general_dataframe
        elif sheet_name == "Exposure information":
            return mock_exposure_dataframe_error

    def validate(self, *args, **kwargs):
        pass


class MockValidator:
    def __init__(self, *args, **kwargs):
        self.report = {'valid': True, 'errors': {}}

    def add_error(self, label, message, field):
        self.report['valid'] = False
        if label not in self.report['errors']:
            self.report['errors'][label] = []
        self.report['errors'][label].append({'message': message, 'field_concerned': field})


@patch('ptmd.lib.validator.core.remove', return_value=None)
@patch('ptmd.lib.validator.core.GoogleDriveConnector', return_value=MockGoogleDriveConnector())
@patch('ptmd.lib.validator.core.validate_identifier')
class TestExcelValidator(TestCase):

    @patch('ptmd.lib.validator.core.get_session', return_value=mocked_session)
    @patch('ptmd.lib.validator.core.ExcelFile', return_value=MockExcelFileSuccess())
    def test_core_success(self, mock_excel_file, mocked_get_session,
                          mocked_validate_identifier, mocked_gdrive_connector, mock_rm):
        validator = ExcelValidator(1)
        validator.validate()
        self.assertEqual(validator.report['valid'], True)

    @patch('ptmd.lib.validator.core.get_session', return_value=mocked_session)
    @patch('ptmd.lib.validator.core.ExcelFile', return_value=MockExcelFileError())
    def test_report_validation_error(self, mock_excel_file, mocked_get_session,
                                     mocked_validate_identifier, mocked_gdrive_connector, mock_rm):
        validator = ExcelValidator(1)
        validator.validate()
        errors = validator.report['errors']
        self.assertEqual(errors['Record at line 3 (FAC002LA1)'],
                         [{'message': 'This field is required.', 'field_concerned': 'exposure_route'}])
        self.assertEqual(validator.report['valid'], False)

    @patch('ptmd.lib.validator.core.get_session', return_value=mocked_session_error)
    def test_report_file_not_found(self, mocked_get_session,
                                   mocked_validate_identifier, mocked_gdrive_connector, mock_rm):
        with self.assertRaises(ValueError) as context:
            validator = ExcelValidator(1)
            validator.validate()
        self.assertEqual('File with ID 1 does not exist.', str(context.exception))


@patch('ptmd.lib.validator.core.GoogleDriveConnector', return_value=MockGoogleDriveConnector())
@patch('ptmd.lib.validator.core.ExternalExcelValidator.validate_file', return_value=None)
@patch('ptmd.lib.validator.core.remove', return_value=None)
class TestExternalValidator(TestCase):

    def test_validator(self, mock_rm, mocked_validate_file, mocked_gdrive_connector):
        validator = ExternalExcelValidator("A")
        validator.validate()
        self.assertEqual(validator.report['valid'], True)


class TestVerticalValidator(TestCase):
    def setUp(self) -> None:
        self.organism: str = "Ethoprophos"
        self.general_information = {
            'timepoints': [4],
            'replicates': 1,
            'blanks': 0,
            'control': 1,
            'compound_vehicle': 'DMSO'
        }
        self.default_node = {
            'data': {
                "compound_name": self.organism,
                "replicate": 1,
                "timepoint (hours)": 4
            },
            'label': 'CP1'
        }

    def test_validate_success(self):
        validator = MockValidator()
        graph = VerticalValidator(self.general_information, validator)
        graph.add_node(self.default_node)
        graph.validate()
        self.assertTrue(validator.report['valid'])

    def test_validate_errors_blanks(self):
        validator = MockValidator()
        self.general_information['blanks'] = 2
        blank_node: dict = deepcopy(self.default_node)
        blank_node['data']['timepoint (hours)'] = 8
        blank_node['data']['compound_name'] = "EXTRACTION BLANK"

        graph = VerticalValidator(self.general_information, validator)
        graph.add_node(self.default_node)
        graph.add_node(blank_node)
        graph.validate()

        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['CP1'][0]['message'],
                         "Extraction blank must have a timepoint of 0.")
        self.assertEqual(validator.report['errors']['Extraction blanks'][0]['message'],
                         "The number of extraction blanks should be 2 but is 1")

    def test_validate_timepoints_missing(self):
        validator = MockValidator()
        self.general_information['timepoints'] = [4, 8]
        graph = VerticalValidator(self.general_information, validator)
        graph.add_node(self.default_node)
        graph.validate()
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors'][self.organism][0]['message'],
                         "Timepoint 1 is missing 1 replicate(s).")

    def test_validate_timepoints_too_many(self):
        validator = MockValidator()
        extra_node: dict = {**self.default_node}
        extra_node['data']['timepoint (hours)'] = 8
        self.general_information['timepoints'] = [4]
        graph = VerticalValidator(self.general_information, validator)
        graph.add_node(self.default_node)
        graph.add_node(extra_node)
        graph.validate()
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors'][self.organism][0]['message'],
                         "Timepoint 1 has greater number of replicates 2 than expected (1).")

    def test_validate_replicate_missing(self):
        validator = MockValidator()
        self.general_information['replicates'] = 2
        graph = VerticalValidator(self.general_information, validator)
        graph.add_node(self.default_node)
        graph.validate()
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors'][self.organism][0]['message'],
                         "Replicate 1 is missing 1 timespoints(s).")

    def test_validate_replicate_too_many(self):
        validator = MockValidator()
        extra_node: dict = {**self.default_node}
        self.general_information['replicates'] = 1
        extra_node['data']['replicate'] = 6
        graph = VerticalValidator(self.general_information, validator)
        graph.add_node(self.default_node)
        graph.add_node(extra_node)
        graph.validate()
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['CP1'][0]['message'],
                         "Replicate 6 is greater than the number of replicates 1.")
        self.assertEqual(validator.report['errors'][self.organism][0]['message'],
                         "Replicate 1 has too many timepoints.")

    def test_validate_controls_dose_not_zero(self):
        validator = MockValidator()
        self.general_information['control'] = 1
        control_node: dict = deepcopy(self.default_node)
        control_node['data']['compound_name'] = "CONTROL (DMSO)"
        control_node['data']['dose_code'] = 1

        graph = VerticalValidator(self.general_information, validator)
        graph.add_node(control_node)
        graph.validate()
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['CP1'][0]['message'], "Controls must have a dose of 0.")
