from unittest import TestCase

from ptmd.api.queries.utils import validate_inputs


class TestUtils(TestCase):

    def test_validate_inputs(self):
        inputs = ['username', 'password']
        user_data = {
            'username': 'test',
            'password': 'test'
        }
        self.assertTrue(validate_inputs(inputs=inputs, data=user_data)[0])
        inputs.append('test')
        valid = validate_inputs(inputs=inputs, data=user_data)
        self.assertFalse(valid[0])
        self.assertEqual(valid[1], 'test')
