from unittest import TestCase
from unittest.mock import patch

from ptmd.database.utils import get_current_user


@patch('ptmd.database.utils.current_user')
class TestUtils(TestCase):

    def test_get_user_valid(self, mock_user):
        mock_user.return_value = 'test'
        self.assertEqual(get_current_user(), 'test')

    def test_get_user_invalid(self, mock_user):
        mock_user.side_effect = RuntimeError('No user')
        self.assertEqual(get_current_user(), None)
