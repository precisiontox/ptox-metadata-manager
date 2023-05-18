from unittest import TestCase
from unittest.mock import patch, mock_open

from ptmd.database import Timepoint


class TestTimepoint(TestCase):

    @patch("builtins.open", mock_open(read_data="{'save_credentials_file': 'test'}"))
    def test_timepoint(self):
        timepoint = Timepoint(value=1, unit='mg/kg', label="BMD10")
        self.assertEqual(dict(timepoint), {'value': 1, 'unit': 'mg/kg', 'label': 'BMD10', 'files': []})
