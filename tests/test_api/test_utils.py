from unittest import TestCase
from unittest.mock import patch

from ptmd.api.queries.utils import user_lookup_callback


@patch('ptmd.api.queries.utils.User')
class TestUserLookupCallback(TestCase):
    def test_lookup(self, mock_user):
        mock_user.query.filter.first.return_value = True
        self.assertTrue(user_lookup_callback({}, {"sub": 1}))
