from unittest import TestCase
from unittest.mock import patch

from ptmd.api.queries.utils import user_lookup_callback, is_allowed


class TestUserLookupCallback(TestCase):

    def test_callback_lookup(self):
        with patch('ptmd.api.queries.utils.User') as mock_user:
            mock_user.query.filter().first.return_value = False
            self.assertFalse(user_lookup_callback({}, {"sub": 1}))

    def test_is_allowed(self):
        self.assertTrue(is_allowed('admin', 'user'))
        self.assertFalse(is_allowed('user', 'admin'))
        self.assertTrue(is_allowed('user', 'disabled'))
        self.assertFalse(is_allowed('banned'))
