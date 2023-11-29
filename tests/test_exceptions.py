from unittest import TestCase

from ptmd.exceptions import APIError


class TestExceptions(TestCase):

    def test_api_error(self):
        with self.assertRaises(SyntaxError) as context:
            APIError()
        self.assertEqual(str(context.exception), 'Cannot instantiate abstract class APIError')
