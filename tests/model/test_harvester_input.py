from os import path
from unittest import TestCase
from datetime import datetime

from dateutil.parser import parse as parse_date

from ptmd.model import HarvesterInput
from ptmd.model.exposure_condition import ExposureCondition
from ptmd.model.const import (
    ALLOWED_PARTNERS,
    ALLOWED_ORGANISMS,
    ALLOWED_CHEMICAL_NAMES,
    ALLOWED_DOSE_VALUES,
    REPLICATES_EXPOSURE_MIN,
    REPLICATES_BLANK_RANGE,
    SAMPLE_SHEET_BASE_COLUMNS
)


PARTNER = ALLOWED_PARTNERS[0]
ORGANISM = ALLOWED_ORGANISMS[0]
CHEMICAL_NAME = ALLOWED_CHEMICAL_NAMES[0]
DOSE_VALUE = ALLOWED_DOSE_VALUES[0]
EXPOSURE_BATCH = 'AA'
REPLICATES_EXPOSURE = 4
REPLICATES_CONTROL = 4
REPLICATES_BLANK = 2
START_DATE = '2018-01-01'
END_DATE = '2019-01-02'
CLASS_NAME = HarvesterInput.__name__


class TestHarvesterInput(TestCase):

    def test_constructor_errors_with_partner(self):
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=1, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        self.assertEqual(CLASS_NAME + ".partner must be a str but got int with value 1", str(context.exception))
        with self.assertRaises(ValueError) as context:
            HarvesterInput(partner='foo', organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        self.assertEqual(CLASS_NAME + ".partner must be one of %s but got %s" % (ALLOWED_PARTNERS, 'foo'),
                         str(context.exception))

    def test_constructor_errors_with_chemical_organism(self):
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER, organism=1, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        self.assertEqual(CLASS_NAME + ".organism must be a str but got int with value 1", str(context.exception))
        with self.assertRaises(ValueError) as context:
            HarvesterInput(partner=PARTNER, organism='foo', exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        self.assertEqual(CLASS_NAME + ".organism must be one of %s but got %s" % (ALLOWED_ORGANISMS, 'foo'),
                         str(context.exception))

    def test_constructor_errors_with_exposure_conditions(self):
        exposure_conditions = [{'foo': 'bar'}]
        error = "__init__() got an unexpected keyword argument 'foo'"
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER,
                           organism=ORGANISM,
                           exposure_conditions=exposure_conditions,
                           exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        self.assertIn(error, str(context.exception))
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER,
                           organism=ORGANISM,
                           exposure_conditions='foo',
                           exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        self.assertEqual("HarvesterInput.exposure must be a list of ExposureCondition or dict but got str with value "
                         "foo", str(context.exception))

        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER,
                           organism=ORGANISM,
                           exposure_conditions=['foo', 'bar'],
                           exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        self.assertEqual("HarvesterInput.exposure must be a list of ExposureCondition or dict but got list "
                         "with value ['foo', 'bar']", str(context.exception))

    def test_constructor_errors_with_exposure_batch(self):
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=1,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        self.assertEqual(CLASS_NAME + ".exposure_batch must be a str but got int with value 1", str(context.exception))
        with self.assertRaises(ValueError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch='foo',
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        self.assertEqual(CLASS_NAME + ".exposure_batch must be one of AA to ZZ but got foo",
                         str(context.exception))

    def test_constructor_error_replicates_exposure(self):
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure='foo', replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        self.assertEqual(CLASS_NAME + ".replicate4exposure must be a int but got str with value foo",
                         str(context.exception))
        with self.assertRaises(ValueError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=0, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        error = '%s.replicate4exposure must be greater than %s but got 0' % (CLASS_NAME, REPLICATES_EXPOSURE_MIN)
        self.assertEqual(error, str(context.exception))

    def test_constructor_error_replicates_control(self):
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control='foo',
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        self.assertEqual(CLASS_NAME + ".replicate4control must be a int but got str with value foo",
                         str(context.exception))
        with self.assertRaises(ValueError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=0,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=END_DATE)
        error = '%s.replicate4control must be greater than %s but got 0' % (CLASS_NAME, REPLICATES_EXPOSURE_MIN)
        self.assertEqual(error, str(context.exception))

    def test_constructor_error_replicate_blank(self):
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank='foo',
                           start_date=START_DATE, end_date=END_DATE)
        self.assertEqual(CLASS_NAME + ".replicate_blank must be a int but got str with value foo",
                         str(context.exception))
        with self.assertRaises(ValueError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=5,
                           start_date=START_DATE, end_date=END_DATE)
        error = "%s.replicate_blank must be between %s and %s but got 5" % (CLASS_NAME,
                                                                            REPLICATES_BLANK_RANGE.min,
                                                                            REPLICATES_BLANK_RANGE.max)
        self.assertEqual(error, str(context.exception))

    def test_constructor_error_start_date(self):
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date='foo', end_date=END_DATE)
        self.assertEqual(CLASS_NAME + ".start_date must be a datetime but got str with value foo",
                         str(context.exception))
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=123, end_date=END_DATE)
        self.assertEqual(CLASS_NAME + ".start_date must be a datetime but got int with value 123",
                         str(context.exception))

    def test_constructor_error_end_date(self):
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date='foo')
        self.assertEqual(CLASS_NAME + ".end_date must be a datetime but got str with value foo",
                         str(context.exception))
        with self.assertRaises(TypeError) as context:
            HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                           replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                           replicate_blank=REPLICATES_BLANK,
                           start_date=START_DATE, end_date=123)
        self.assertEqual(CLASS_NAME + ".end_date must be a datetime but got int with value 123",
                         str(context.exception))

    def test_constructor_success(self):
        exposure_conditions = [{'chemical_name': CHEMICAL_NAME, 'dose': DOSE_VALUE}]
        expected_exposure_conditions = [ExposureCondition(**exposure_conditions[0])]
        harvester = HarvesterInput(partner=PARTNER,
                                   organism=ORGANISM,
                                   exposure_conditions=exposure_conditions,
                                   exposure_batch=EXPOSURE_BATCH,
                                   replicate4exposure=REPLICATES_EXPOSURE,
                                   replicate4control=REPLICATES_CONTROL,
                                   replicate_blank=REPLICATES_BLANK,
                                   start_date=START_DATE, end_date=END_DATE)
        self.assertEqual(ALLOWED_PARTNERS[0], harvester.partner)
        self.assertEqual(ALLOWED_ORGANISMS[0], harvester.organism)
        self.assertEqual(expected_exposure_conditions, harvester.exposure_conditions)
        self.assertEqual(EXPOSURE_BATCH, harvester.exposure_batch)
        self.assertEqual(REPLICATES_EXPOSURE, harvester.replicate4exposure)
        self.assertEqual(REPLICATES_CONTROL, harvester.replicate4control)
        self.assertEqual(REPLICATES_BLANK, harvester.replicate_blank)
        self.assertIsInstance(harvester.start_date, datetime)

    def test_add_exposure_batch(self):
        exposure_conditions = [{'chemical_name': CHEMICAL_NAME, 'dose': DOSE_VALUE}]
        exposure_condition = ExposureCondition(**exposure_conditions[0])
        harvester = HarvesterInput(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                                   replicate4exposure=REPLICATES_EXPOSURE,
                                   replicate4control=REPLICATES_CONTROL,
                                   replicate_blank=REPLICATES_BLANK,
                                   start_date=START_DATE, end_date=END_DATE)

        harvester.add_exposure_condition(exposure_conditions[0])
        self.assertEqual([exposure_condition], harvester.exposure_conditions)

        harvester.add_exposure_condition(exposure_condition)
        self.assertEqual([exposure_condition, exposure_condition], harvester.exposure_conditions)

        with self.assertRaises(ValueError) as context:
            harvester.add_exposure_condition('foo')
        self.assertEqual(
            "The exposure condition must be a dict or an ExposureCondition object",
            str(context.exception))

    def test_to_dict(self):
        exposure_condition = {'chemical_name': CHEMICAL_NAME, 'dose': DOSE_VALUE}
        expected = {
            'partner': PARTNER, 'organism': ORGANISM, 'exposure_conditions': [exposure_condition],
            'exposure_batch': EXPOSURE_BATCH,
            'replicate4exposure': REPLICATES_EXPOSURE,
            'replicate4control': REPLICATES_CONTROL,
            'replicate_blank': REPLICATES_BLANK,
            'start_date': START_DATE, 'end_date': END_DATE
        }
        start_date = parse_date(START_DATE)
        end_date = parse_date(END_DATE)
        exposure_conditions = [ExposureCondition(**exposure_condition)]
        harvester = HarvesterInput(partner=PARTNER,
                                   organism=ORGANISM,
                                   exposure_conditions=exposure_conditions,
                                   exposure_batch=EXPOSURE_BATCH,
                                   replicate4exposure=REPLICATES_EXPOSURE,
                                   replicate4control=REPLICATES_CONTROL,
                                   replicate_blank=REPLICATES_BLANK,
                                   start_date=start_date, end_date=end_date)
        self.assertEqual(expected, dict(harvester))

    def test_to_dataframe(self):
        harvester = HarvesterInput(partner=PARTNER,
                                   organism=ORGANISM,
                                   exposure_conditions=[
                                       ExposureCondition(**{'chemical_name': CHEMICAL_NAME, 'dose': DOSE_VALUE})
                                   ],
                                   exposure_batch=EXPOSURE_BATCH,
                                   replicate4exposure=REPLICATES_EXPOSURE,
                                   replicate4control=REPLICATES_CONTROL,
                                   replicate_blank=REPLICATES_BLANK,
                                   start_date=START_DATE, end_date=END_DATE)
        sample_dataframe = harvester.to_dataframe()
        for col in SAMPLE_SHEET_BASE_COLUMNS:
            self.assertIn(col, sample_dataframe.columns)
        self.assertEqual(1, len(sample_dataframe.index))
        self.assertEqual(len(sample_dataframe.iloc[0]), len(SAMPLE_SHEET_BASE_COLUMNS))

    def test_save(self):
        here = path.dirname(path.abspath(__file__))
        output_path = path.join(here, '..', 'data', 'excel', 'test.xlsx')
        harvester = HarvesterInput(partner=PARTNER,
                                   organism=ORGANISM,
                                   exposure_conditions=[
                                       ExposureCondition(**{'chemical_name': CHEMICAL_NAME, 'dose': DOSE_VALUE})
                                   ],
                                   exposure_batch=EXPOSURE_BATCH,
                                   replicate4exposure=REPLICATES_EXPOSURE,
                                   replicate4control=REPLICATES_CONTROL,
                                   replicate_blank=REPLICATES_BLANK,
                                   start_date=START_DATE, end_date=END_DATE)
        file_path = harvester.save(output_path)
        assert path.exists(file_path)
