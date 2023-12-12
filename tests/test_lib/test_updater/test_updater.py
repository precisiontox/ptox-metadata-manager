from unittest import TestCase
from unittest.mock import patch

from pandas import DataFrame

from ptmd.lib import BatchUpdater, BatchError
from ptmd.const import PTX_ID_LABEL


class MockedFile:
    def __init__(self, batch, shipped):
        self.batch = batch
        self.shipped = shipped
        self.author_id = 1
        self.gdrive_id = "test"
        self.organism = type('Organism', (), {'ptox_biosystem_name': 'test'})
        self.name = "test"


def read_excel_side_effect(filepath, sheet_name):
    if sheet_name == "General Information":
        return DataFrame(
            data=[["UOX", "AA"]],
            columns=["partner_id", "exposure_batch"]
        )
    elif sheet_name == "Exposure information":
        return DataFrame(
            data=[["RAA002LA1"]],
            columns=[PTX_ID_LABEL]
        )


class TestBatchUpdater(TestCase):

    def test_batch_constructor_errors_too_many_inputs(self):
        with self.assertRaises(ValueError) as context:
            BatchUpdater(batch="test", file_id=1, filepath="test")
        self.assertEqual(str(context.exception), "Provide only one file_id or filepath, not both")

    def test_batch_constructor_errors_not_enough_input(self):
        with self.assertRaises(ValueError) as context:
            BatchUpdater(batch="test")
        self.assertEqual(str(context.exception), "Provide a file_id or filepath")

    @patch('ptmd.lib.updater.batch.read_excel', side_effect=read_excel_side_effect)
    @patch('ptmd.lib.updater.batch.save_to_excel')
    def test_modify_in_file(self, mock_save_excel, mock_read_excel):
        batch_updater = BatchUpdater(batch="AB", filepath="test")
        self.assertEqual(batch_updater.old_batch, "AA")
        self.assertEqual(batch_updater.new_batch, "AB")
        self.assertFalse(hasattr(batch_updater, "file_id"))

    @patch('ptmd.lib.updater.batch.BatchUpdater.modify_in_file')
    @patch('ptmd.lib.updater.batch.File')
    @patch('ptmd.lib.updater.batch.session')
    @patch('ptmd.lib.updater.batch.get_current_user')
    @patch('ptmd.lib.updater.batch.get_shipped_file')
    @patch('ptmd.lib.updater.batch.GoogleDriveConnector')
    @patch('ptmd.lib.updater.batch.remove')
    def test_modify_in_db_success(self, mock_rm, mock_gdrive, mocked_shipped_file,
                                  mock_get_current_user, mock_session, mock_file, mock_modify_in_file):
        mock_modify_in_file.return_value = "AA"
        mock_file.query.filter_by().first.return_value = MockedFile(batch="AA", shipped=False)
        mock_get_current_user.return_value.role = "admin"
        mocked_shipped_file.return_value = True
        batch_updater = BatchUpdater(batch="AB", file_id=1)
        mock_session.commit.assert_called_once()
        mock_rm.assert_called_with(mock_gdrive().download_file())
        self.assertEqual(batch_updater.file.batch, "AB")
        self.assertEqual(batch_updater.old_batch, "AA")

    @patch('ptmd.lib.updater.batch.File')
    @patch('ptmd.lib.updater.batch.jsonify')
    def test_modify_in_db_error_404(self, mock_jsonify, mock_file):
        mock_file.query.filter_by().first.return_value = None

        with self.assertRaises(BatchError) as context:
            BatchUpdater(batch="AB", file_id=1)
        self.assertEqual(str(context.exception), "No file found")
        self.assertEqual(context.exception.code, 404)

        context.exception.serialize()
        mock_jsonify.assert_called_with({"message": "No file found"})

    @patch('ptmd.lib.updater.batch.File')
    def test_modify_in_db_error_400_same_batch(self, mock_file):
        mock_file.query.filter_by().first.return_value = MockedFile(batch="AB", shipped=True)
        with self.assertRaises(BatchError) as context:
            BatchUpdater(batch="AB", file_id=1)
        self.assertEqual(str(context.exception),
                         "Could not update: the new batch and old batch have the same value")
        self.assertEqual(context.exception.code, 400)

    @patch('ptmd.lib.updater.batch.File')
    def test_modify_in_db_error_400_shipped(self, mock_file):
        mock_file.query.filter_by().first.return_value = MockedFile(batch="AC", shipped=True)
        with self.assertRaises(BatchError) as context:
            BatchUpdater(batch="AB", file_id=1)
        self.assertEqual(str(context.exception), "File already shipped")
        self.assertEqual(context.exception.code, 400)

    @patch('ptmd.lib.updater.batch.File')
    @patch('ptmd.lib.updater.batch.get_current_user')
    def test_modify_in_db_error_403(self, mock_user, mock_file):
        mock_file.query.filter_by().first.return_value = MockedFile(batch="AC", shipped=False)
        mock_user.return_value.role = "user"
        mock_user.return_value.id = 2
        with self.assertRaises(BatchError) as context:
            BatchUpdater(batch="AB", file_id=1)
        self.assertEqual(str(context.exception), "You are authorized to do this")
        self.assertEqual(context.exception.code, 403)

    @patch('ptmd.lib.updater.batch.File')
    @patch('ptmd.lib.updater.batch.get_current_user')
    @patch('ptmd.lib.updater.batch.get_shipped_file', return_value=True)
    def test_modify_in_db_error_412(self, mock_shipped_file, mock_user, mock_file):
        mock_file.query.filter_by().first.return_value = MockedFile(batch="AC", shipped=False)
        mock_user.return_value.role = "admin"
        mock_user.return_value.id = 1
        with self.assertRaises(BatchError) as context:
            BatchUpdater(batch=None, file_id=1)
        self.assertEqual(str(context.exception), "Batch already used with test")
        self.assertEqual(context.exception.code, 412)

    @patch('ptmd.lib.updater.batch.File')
    @patch('ptmd.lib.updater.batch.get_current_user')
    @patch('ptmd.lib.updater.batch.get_shipped_file', return_value=True)
    @patch('ptmd.lib.updater.batch.GoogleDriveConnector')
    @patch('ptmd.lib.updater.batch.session')
    def test_modify_in_db_error_500(self, mock_session, mock_gdrive, mock_shipped_file, mock_user, mock_file):
        mock_gdrive.return_value.side_effect = Exception('test')
        mock_file.query.filter_by().first.return_value = MockedFile(batch="AC", shipped=False)
        mock_user.return_value.role = "admin"
        mock_user.return_value.id = 1
        with self.assertRaises(BatchError):
            BatchUpdater(batch="AA", file_id=1)
        mock_session.rollback.assert_called_once()
