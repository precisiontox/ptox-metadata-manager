from unittest import TestCase
from unittest.mock import patch


from ptmd.database.queries import create_timepoints_hours
from ptmd.exceptions import TimepointValueError


class TestCreateTimepointsHours(TestCase):

    @patch('ptmd.database.queries.timepoints.session')
    def test_create_timepoints_hours(self, mock_session):
        timepoints = create_timepoints_hours([1, 2])
        mock_session.commit.assert_called()
        self.assertEqual(mock_session.add.call_count, 2)
        self.assertEqual(dict(timepoints[0]), {'value': 1, 'unit': 'hours', 'label': 'TP1', 'files': []})
        self.assertEqual(dict(timepoints[1]), {'value': 2, 'unit': 'hours', 'label': 'TP2', 'files': []})

    def test_create_timepoint_errors(self):
        with self.assertRaises(TimepointValueError) as context:
            create_timepoints_hours([None, 1])
        self.assertTrue('Timepoint value must be a positive integer' in str(context.exception))
