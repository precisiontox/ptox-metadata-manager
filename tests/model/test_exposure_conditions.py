from unittest import TestCase
from unittest.mock import patch

from ptmd.model.exposure_condition import ExposureCondition
from ptmd.const import ALLOWED_CHEMICAL_NAMES, ALLOWED_DOSE_VALUES


CHEMICAL_NAME = ALLOWED_CHEMICAL_NAMES[0]
DOSE_VALUE = ALLOWED_DOSE_VALUES[0]


@patch('ptmd.model.exposure_condition.get_allowed_chemicals', return_value=ALLOWED_CHEMICAL_NAMES)
class TestExposureCondition(TestCase):

    def test_constructor_errors_with_chemicals_name(self, mock_allowed_chemicals):
        with self.assertRaises(TypeError) as context:
            ExposureCondition(chemicals_name=1, dose=[DOSE_VALUE])
        self.assertEqual("chemicals_name must be a list but got int with value 1", str(context.exception))
        with self.assertRaises(ValueError) as context:
            ExposureCondition(chemicals_name=['foo'], dose=DOSE_VALUE)
        self.assertEqual("chemicals_name must be one of ['chemical1', 'chemical2', 'chemical3'] but got foo",
                         str(context.exception))
        with self.assertRaises(TypeError) as context:
            ExposureCondition(chemicals_name=[1], dose=DOSE_VALUE)
        self.assertEqual("chemicals_name must be a str but got int with value 1", str(context.exception))

    def test_constructor_errors_with_chemical_dose(self, mock_allowed_chemicals):
        with self.assertRaises(TypeError) as context:
            ExposureCondition(chemicals_name=[CHEMICAL_NAME], dose=1)
        self.assertEqual("dose must be a str but got int with value 1", str(context.exception))
        with self.assertRaises(TypeError) as context:
            ExposureCondition(chemicals_name=[CHEMICAL_NAME], dose=['foo'])
        self.assertEqual("dose must be a str but got list with value ['foo']", str(context.exception))

    def test_constructor_success(self, mock_allowed_chemicals):
        ec = ExposureCondition([CHEMICAL_NAME], DOSE_VALUE)
        self.assertEqual([CHEMICAL_NAME], ec.chemicals_name)
        self.assertEqual(DOSE_VALUE, ec.dose)

    def test_comparators(self, mock_allowed_chemicals):
        ec_1 = ExposureCondition([CHEMICAL_NAME], DOSE_VALUE)
        ec_2 = ExposureCondition(ALLOWED_CHEMICAL_NAMES, ALLOWED_DOSE_VALUES[1])
        ec_3 = ExposureCondition([CHEMICAL_NAME], DOSE_VALUE)
        self.assertNotEqual(ec_1, ec_2)
        self.assertEqual(ec_1, ec_3)
