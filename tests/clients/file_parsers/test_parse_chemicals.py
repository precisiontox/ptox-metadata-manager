from unittest import TestCase

from numpy import NaN

from ptmd.clients.file_parsers.parse_chemicals import Compound, parse_chemicals


class TestCompound(TestCase):

    def test_parse_chemical(self):
        chemicals = parse_chemicals()
        keys = ['common_name', 'ptx_code', 'formula', 'name_hash_id']
        for chemical in chemicals:
            for key in keys:
                self.assertIn(key, chemical.keys())
            self.assertEqual(type(chemical), dict)

    def test_compound(self):
        data = {
            'ptx_code': 'PTX0001',
            'name': 'Acetic acid',
            'cas': '64-19-7',
            'formula': 'CH3COOH'
        }
        compound = Compound(**data)
        self.assertEqual(compound.ptx_code, 1)
        self.assertEqual(compound.common_name, 'Acetic acid')
        self.assertEqual(compound.cas, '64-19-7')
        self.assertEqual(compound.formula, 'CH3COOH')
        name = data['name']
        hash_id = data['cas']
        del data['name']
        del data['cas']
        data['ptx_code'] = 1
        data['common_name'] = name
        data['name_hash_id'] = hash_id
        self.assertEqual(dict(compound), data)

    def test_compound_errors(self):
        data = {
            'ptx_code': NaN,
            'name': 'Acetic acid',
            'cas': '64-19-7',
            'formula': 'CH3COOH'
        }
        with self.assertRaises(ValueError) as context:
            Compound(**data)
        self.assertEqual(str(context.exception), 'ptx_code cannot be nan for compound Acetic acid')

        data['ptx_code'] = '-'
        with self.assertRaises(ValueError) as context:
            Compound(**data)
        self.assertEqual(str(context.exception),
                         'ptx_code needs to be a valid string but got "-" for compound Acetic acid')

        data['ptx_code'] = 'PTX0001'
        data['cas'] = NaN
        with self.assertRaises(ValueError) as context:
            Compound(**data)
        self.assertEqual(str(context.exception), 'CAS cannot be nan for compound Acetic acid')

        data['cas'] = '64-19-7'
        data['formula'] = NaN
        with self.assertRaises(ValueError) as context:
            Compound(**data)
        self.assertEqual(str(context.exception), 'formula cannot be nan for compound Acetic acid')
