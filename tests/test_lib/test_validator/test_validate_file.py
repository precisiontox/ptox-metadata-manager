from unittest import TestCase
from unittest.mock import patch

from pandas import DataFrame, Series, concat

from ptmd.lib.validator.core import ExcelValidator
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
MOCKED_FILE = {'gdrive_id': '1', 'name': 'test.xlsx', 'file_id': 1}


@patch('ptmd.lib.validator.core.session')
@patch('ptmd.lib.validator.core.validate_identifier')
@patch('ptmd.lib.validator.core.GoogleDriveConnector', return_value=MockGoogleDriveConnector())
@patch('ptmd.lib.validator.core.remove')
class TestExcelValidator(TestCase):

    @patch('ptmd.lib.validator.core.ExcelFile', return_value=MockExcelFileSuccess())
    def test_core_success(self, mock_rm, mock_excel_file, mocked_get_session,
                          mocked_validate_identifier, mocked_gdrive_connector):
        with patch('ptmd.lib.validator.core.File') as mocked_file:
            mocked_file.query.filter().first.return_value = MOCKED_FILE
            validator = ExcelValidator(1)
            validator.validate()
            self.assertEqual(validator.report['valid'], True)

    @patch('ptmd.lib.validator.core.ExcelFile', return_value=MockExcelFileError())
    def test_report_validation_error(self, mock_rm, mock_excel_file, mocked_get_session,
                                     mocked_validate_identifier, mocked_gdrive_connector):
        with patch('ptmd.lib.validator.core.File') as mocked_file:
            mocked_file.query.filter().first.return_value = MOCKED_FILE
            validator = ExcelValidator(1)
            validator.validate()
            errors = validator.report['errors']
            self.assertEqual(errors['Record at line 3 (FAC002LA1)'],
                             [{'message': 'This field is required.', 'field_concerned': 'exposure_route'}])
            self.assertEqual(validator.report['valid'], False)

    def test_report_file_not_found(self, mocked_get_session, mocked_validate_identifier, mocked_gdrive_connector,
                                   mock_rm):
        with patch('ptmd.lib.validator.core.File') as mocked_file:
            mocked_file.query.filter().first.return_value = None
            with self.assertRaises(ValueError) as context:
                validator = ExcelValidator(1)
                validator.validate()
            self.assertEqual('File with ID 1 does not exist.', str(context.exception))