from unittest import TestCase
from unittest.mock import patch
from copy import deepcopy

from pandas import DataFrame, Series, concat

from ptmd.lib.validator.core import ExternalExcelValidator, VerticalValidator
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
    "qsd", "qsd", "qsd", "qsd", "qsd", 12, 12, 1, "A", 1, None, None, None,
    1, "Ethoprophos", "BMD10", "TP1", 4, "FAC002LA1"
], index=SAMPLE_SHEET_COLUMNS)
mock_exposure_dataframe = concat([mock_exposure_dataframe, mock_exposure_series.to_frame().T],
                                 ignore_index=False, sort=False, copy=False)
mock_exposure_series_error = Series([
    "qsd", "qsd", "qsd", None, "qsd", 12, 12, 1, "A", 1, None, None, None,
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


MOCKED_FILE = {'gdrive_id': '1', 'name': 'test.xlsx', 'file_id': 1}


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
                "timepoint_(hours)": 4
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
        blank_node['data']['timepoint_(hours)'] = 8
        blank_node['data']['compound_name'] = "EXTRACTION BLANK"
        blank_node['data']['collection_order'] = 10
        blank_node['data']['box_id'] = "Box1"

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
        self.general_information['timepoints'] = [0, 1]
        graph = VerticalValidator(self.general_information, validator)
        graph.add_node(self.default_node)
        graph.validate()
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors'][self.organism][0]['message'],
                         "Timepoint 1 is missing 1 replicate(s).")

    def test_validate_timepoints_too_many(self):
        validator = MockValidator()
        extra_node: dict = {**self.default_node}
        extra_node['data']['timepoint_(hours)'] = 8
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
        control_node['data']['timepoint_(hours)'] = 4

        graph = VerticalValidator(self.general_information, validator)
        graph.add_node(control_node)
        graph.validate()
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors']['CP1'][0]['message'], "Controls must have a dose of 0.")

    def test_validate_failed_box_id(self):
        validator = MockValidator()
        info = deepcopy(self.general_information)
        info['replicates'] = 2
        graph = VerticalValidator(info, validator)

        node_1: dict = deepcopy(self.default_node)
        node_1['data']['box_id'] = "Box1"
        node_1['data']['box_column'] = 1
        node_1['data']['box_row'] = 'A'

        node_2: dict = deepcopy(self.default_node)
        node_2['data']['replicate'] = 2
        node_2['data']['box_id'] = "Box1"
        node_2['data']['box_column'] = 1
        node_2['data']['box_row'] = 'A'

        graph.add_node(node_1)
        graph.add_node(node_2)
        graph.validate()
        expected_error = {
            'CP1': [
                {'message': 'Box position Box1_A_1 is already used.', 'field_concerned': 'box_position'},
                {'message': 'Collection order None is already used.', 'field_concerned': 'collection_order'}
            ]
        }
        self.assertFalse(validator.report['valid'])
        self.assertEqual(validator.report['errors'], expected_error)
