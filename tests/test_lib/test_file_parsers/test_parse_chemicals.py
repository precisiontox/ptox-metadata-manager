from unittest import TestCase

from ptmd.lib.file_parsers.parse_chemicals import parse_chemicals


class TestCompound(TestCase):

    def test_parse_chemical(self):
        chemicals = parse_chemicals()
        keys = ['common_name', 'ptx_code', 'formula', 'cas']
        for chemical in chemicals:
            for key in keys:
                self.assertIn(key, chemical.keys())
            self.assertEqual(type(chemical), dict)
