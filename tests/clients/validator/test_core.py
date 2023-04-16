from unittest import TestCase
from unittest.mock import patch

from pandas import DataFrame, Series, concat

from ptmd.clients.validator.core import ExcelValidator
from ptmd.const import SAMPLE_SHEET_COLUMNS, GENERAL_SHEET_COLUMNS


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
    def first(self):
        return None


class MockGoogleDriveConnector:
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
    ["UOB", "Drosophila_melanogaster_female", "AC", "4", "4", "2", "2020-01-01", "2020-10-01", [4, 12, 36], "DMSO"],
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


class MockExcelFileError:
    def __init__(self, *args, **kwargs):
        pass

    def parse(self, sheet_name, *args, **kwargs):
        if sheet_name == "General Information":
            return mock_general_dataframe
        elif sheet_name == "Exposure information":
            return mock_exposure_dataframe_error


@patch('ptmd.clients.validator.core.remove', return_value=None)
@patch('ptmd.clients.validator.core.GoogleDriveConnector', return_value=MockGoogleDriveConnector())
@patch('ptmd.clients.validator.core.validate_identifier')
class TestExcelValidator(TestCase):

    @patch('ptmd.clients.validator.core.get_session', return_value=mocked_session)
    @patch('ptmd.clients.validator.core.ExcelFile', return_value=MockExcelFileSuccess())
    def test_core_success(self, mock_excel_file, mocked_get_session,
                          mocked_validate_identifier, mocked_gdrive_connector, mock_rm):
        validator = ExcelValidator(1)
        self.assertEqual(validator.report['valid'], True)

    @patch('ptmd.clients.validator.core.get_session', return_value=mocked_session)
    @patch('ptmd.clients.validator.core.ExcelFile', return_value=MockExcelFileError())
    def test_report_validation_error(self, mock_excel_file, mocked_get_session,
                                     mocked_validate_identifier, mocked_gdrive_connector, mock_rm):
        validator = ExcelValidator(1)
        errors = validator.report['errors']
        self.assertEqual(errors['Record at line 3 (FAC002LA1)'],
                         [{'message': 'This field is required.', 'field_concerned': 'exposure_route'}])
        self.assertEqual(validator.report['valid'], False)

    @patch('ptmd.clients.validator.core.get_session', return_value=mocked_session_error)
    def test_report_file_not_found(self, mocked_get_session,
                                   mocked_validate_identifier, mocked_gdrive_connector, mock_rm):
        with self.assertRaises(ValueError) as context:
            ExcelValidator(1)
        self.assertEqual('File with ID 1 does not exist.', str(context.exception))
