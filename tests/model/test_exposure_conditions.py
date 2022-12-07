from unittest import TestCase

from ptmd.model.exposure_condition import ExposureCondition
from ptmd.const import ALLOWED_CHEMICAL_NAMES, ALLOWED_DOSE_VALUES


CHEMICAL_NAME = ALLOWED_CHEMICAL_NAMES[0]
DOSE_VALUE = ALLOWED_DOSE_VALUES[0]
CLASS_NAME = ExposureCondition.__name__


class TestExposureCondition(TestCase):

    def test_constructor_errors_with_chemical_name(self):
        with self.assertRaises(TypeError) as context:
            ExposureCondition(chemical_name=1, dose=DOSE_VALUE)
        self.assertEqual(CLASS_NAME + ".chemical_name must be a str but got int with value 1", str(context.exception))
        with self.assertRaises(ValueError) as context:
            ExposureCondition(chemical_name='foo', dose=DOSE_VALUE)
        self.assertEqual(CLASS_NAME + ".chemical_name must be one of %s but got %s" % (
            ALLOWED_CHEMICAL_NAMES, 'foo'), str(context.exception))

    def test_constructor_errors_with_chemical_dose(self):
        with self.assertRaises(TypeError) as context:
            ExposureCondition(chemical_name=CHEMICAL_NAME, dose=1)
        self.assertEqual(CLASS_NAME + ".dose must be a str but got int with value 1", str(context.exception))
        with self.assertRaises(ValueError) as context:
            ExposureCondition(chemical_name=CHEMICAL_NAME, dose='foo')
        self.assertEqual(CLASS_NAME + ".dose must be one of %s but got %s" % (ALLOWED_DOSE_VALUES, 'foo'), str(context.exception))

    def test_constructor_success(self):
        ec = ExposureCondition(CHEMICAL_NAME, DOSE_VALUE)
        self.assertEqual(CHEMICAL_NAME, ec.chemical_name)
        self.assertEqual(DOSE_VALUE, ec.dose)

    def test_comparators(self):
        ec_1 = ExposureCondition(CHEMICAL_NAME, DOSE_VALUE)
        ec_2 = ExposureCondition(ALLOWED_CHEMICAL_NAMES[1], ALLOWED_DOSE_VALUES[1])
        ec_3 = ExposureCondition(CHEMICAL_NAME, DOSE_VALUE)
        self.assertNotEqual(ec_1, ec_2)
        self.assertEqual(ec_1, ec_3)
