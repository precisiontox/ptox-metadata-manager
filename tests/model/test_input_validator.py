from os import path
from unittest import TestCase
from unittest.mock import patch
from datetime import datetime

from dateutil.parser import parse as parse_date

from ptmd.model import Inputs2Dataframes, ExposureCondition
from ptmd.const import (
    ALLOWED_PARTNERS,
    ALLOWED_DOSE_VALUES,
    REPLICATES_EXPOSURE_MIN,
    REPLICATES_BLANK_RANGE,
    SAMPLE_SHEET_COLUMNS,
    GENERAL_SHEET_COLUMNS,
    TIMEPOINTS_RANGE, ALLOWED_VEHICLES
)

ALLOWED_ORGANISMS = ["organism1", "organism2", "organism3"]
ALLOWED_CHEMICAL_NAMES = ["chemical1", "chemical2", "chemical3"]
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
HERE = path.dirname(path.abspath(__file__))
EXPOSURE_CONDITIONS = [{'chemicals_name': [CHEMICAL_NAME], 'dose': DOSE_VALUE}]
TIMEPOINTS = 3
VEHICLE = ALLOWED_VEHICLES[0]


@patch('ptmd.model.inputs2dataframes.get_allowed_organisms', return_value=ALLOWED_ORGANISMS)
@patch('ptmd.model.exposure_condition.get_allowed_chemicals', return_value=ALLOWED_CHEMICAL_NAMES)
class TestInputsToDataframesErrors(TestCase):
    def test_constructor_errors_with_partner(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=1, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("partner must be a str but got int with value 1", str(context.exception))
        with self.assertRaises(ValueError) as context:
            Inputs2Dataframes(partner='foo', organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("partner must be one of %s but got %s" % (ALLOWED_PARTNERS, 'foo'),
                         str(context.exception))

    def test_constructor_errors_with_chemical_organism(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=1, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("organism must be a str but got int with value 1", str(context.exception))
        with self.assertRaises(ValueError) as context:
            Inputs2Dataframes(partner=PARTNER, organism='foo', exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("organism must be one of %s but got %s" % (ALLOWED_ORGANISMS, 'foo'),
                         str(context.exception))

    def test_constructor_errors_with_exposure_conditions(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        error = "__init__() got an unexpected keyword argument 'foo'"
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER,
                              organism=ORGANISM,
                              exposure_conditions=[{'foo': 'bar'}],
                              exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertIn(error, str(context.exception))
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER,
                              organism=ORGANISM,
                              exposure_conditions='foo',
                              exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("exposure must be a list of ExposureCondition or dict but got str with value "
                         "foo", str(context.exception))

        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER,
                              organism=ORGANISM,
                              exposure_conditions=['foo', 'bar'],
                              exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("exposure must be a list of ExposureCondition or dict but got list "
                         "with value ['foo', 'bar']", str(context.exception))

    def test_constructor_errors_with_exposure_batch(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=1,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("exposure_batch must be a str but got int with value 1", str(context.exception))
        with self.assertRaises(ValueError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch='fo',
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("exposure_batch must be one of AA to ZZ but got fo",
                         str(context.exception))
        with self.assertRaises(ValueError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch='AAA',
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("exposure_batch must be less than 2 characters but got 3 (value: AAA)",
                         str(context.exception))

    def test_constructor_error_replicates_exposure(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure='foo', replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("replicate4exposure must be a int but got str with value foo",
                         str(context.exception))
        with self.assertRaises(ValueError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=0, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        error = 'replicate4exposure must be greater than %s but got 0' % REPLICATES_EXPOSURE_MIN
        self.assertEqual(error, str(context.exception))

    def test_constructor_error_replicates_control(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control='foo',
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("replicate4control must be a int but got str with value foo",
                         str(context.exception))
        with self.assertRaises(ValueError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=0,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        error = 'replicate4control must be greater than %s but got 0' % REPLICATES_EXPOSURE_MIN
        self.assertEqual(error, str(context.exception))

    def test_constructor_error_replicate_blank(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank='foo', vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("replicate_blank must be a int but got str with value foo",
                         str(context.exception))
        with self.assertRaises(ValueError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=5, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        error = "replicate_blank must be between %s and %s but got 5" % (REPLICATES_BLANK_RANGE.min,
                                                                         REPLICATES_BLANK_RANGE.max)
        self.assertEqual(error, str(context.exception))

    def test_constructor_error_start_date(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date='foo', end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("start_date must be a datetime but got str with value foo",  str(context.exception))
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=123, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("start_date must be a datetime but got int with value 123",
                         str(context.exception))

    def test_constructor_error_end_date(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date='foo', timepoints=TIMEPOINTS)
        self.assertEqual("end_date must be a datetime but got str with value foo", str(context.exception))
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=123, timepoints=TIMEPOINTS)
        self.assertEqual("end_date must be a datetime but got int with value 123",
                         str(context.exception))

    def test_constructor_error_timepoints(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints='foo')
        self.assertEqual("timepoints must be a int but got str with value foo", str(context.exception))
        with self.assertRaises(ValueError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=100)
        error = "timepoints must be between %s and %s but got 100" % (TIMEPOINTS_RANGE.min, TIMEPOINTS_RANGE.max)
        self.assertEqual(error, str(context.exception))

    def test_constructor_error_vehicle(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=123,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("vehicle must be a str but got int with value 123", str(context.exception))
        with self.assertRaises(ValueError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle='foo',
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS)
        self.assertEqual("vehicle must be one of %s but got foo" % ALLOWED_VEHICLES, str(context.exception))

    def test_constructor_error_tp0(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        with self.assertRaises(TypeError) as context:
            Inputs2Dataframes(partner=PARTNER, organism=ORGANISM, exposure_batch=EXPOSURE_BATCH,
                              replicate4exposure=REPLICATES_EXPOSURE, replicate4control=REPLICATES_CONTROL,
                              replicate_blank=REPLICATES_BLANK, vehicle=VEHICLE,
                              start_date=START_DATE, end_date=END_DATE, timepoints=TIMEPOINTS,
                              timepoint_zero='foo')
        self.assertEqual("timepoint_zero must be a bool but got str with value foo", str(context.exception))

    def test_constructor_success(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        exposure_conditions = [ExposureCondition(**EXPOSURE_CONDITIONS[0])]
        harvester = make_harvester()
        self.assertEqual(ALLOWED_PARTNERS[0], harvester.partner)
        self.assertEqual(ALLOWED_ORGANISMS[0], harvester.organism)
        self.assertEqual(VEHICLE, harvester.vehicle)
        self.assertEqual(exposure_conditions, harvester.exposure_conditions)
        self.assertEqual(EXPOSURE_BATCH, harvester.exposure_batch)
        self.assertEqual(REPLICATES_EXPOSURE, harvester.replicate4exposure)
        self.assertEqual(REPLICATES_CONTROL, harvester.replicate4control)
        self.assertEqual(REPLICATES_BLANK, harvester.replicate_blank)
        self.assertIsInstance(harvester.start_date, datetime)

    def test_add_exposure_batch(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        exposure_conditions = [ExposureCondition(**EXPOSURE_CONDITIONS[0])]
        harvester = make_harvester()
        harvester.add_exposure_condition(EXPOSURE_CONDITIONS[0])
        self.assertEqual([*exposure_conditions, *exposure_conditions], harvester.exposure_conditions)
        harvester.add_exposure_condition(exposure_conditions[0])
        self.assertEqual([*exposure_conditions, *exposure_conditions, *exposure_conditions],
                         harvester.exposure_conditions)
        with self.assertRaises(ValueError) as context:
            harvester.add_exposure_condition('foo')
        self.assertEqual("The exposure condition must be a dict or an ExposureCondition object", str(context.exception))

    def test_to_dict(self, mock_get_allowed_chemicals, mock_allowed_organisms):
        exposure_conditions = [ExposureCondition(**EXPOSURE_CONDITIONS[0])]
        expected = {
            'partner': PARTNER,
            'organism': ORGANISM,
            'exposure_conditions': EXPOSURE_CONDITIONS,
            'exposure_batch': EXPOSURE_BATCH,
            'replicate4exposure': REPLICATES_EXPOSURE,
            'replicate4control': REPLICATES_CONTROL,
            'replicate_blank': REPLICATES_BLANK,
            'start_date': START_DATE,
            'end_date': END_DATE,
            'timepoints': 3,
            "vehicle": VEHICLE
        }
        start_date = parse_date(START_DATE)
        end_date = parse_date(END_DATE)
        harvester = Inputs2Dataframes(partner=PARTNER,
                                      organism=ORGANISM,
                                      exposure_conditions=exposure_conditions,
                                      exposure_batch=EXPOSURE_BATCH,
                                      replicate4exposure=REPLICATES_EXPOSURE,
                                      replicate4control=REPLICATES_CONTROL,
                                      replicate_blank=REPLICATES_BLANK,
                                      start_date=start_date,
                                      end_date=end_date, vehicle=VEHICLE,
                                      timepoints=TIMEPOINTS)
        self.assertEqual(expected, dict(harvester))
        self.assertFalse(harvester.timepoint_zero)

    @patch('ptmd.model.inputs2dataframes.get_organism_code', return_value="X")
    @patch('ptmd.model.inputs2dataframes.get_chemical_code_mapping', return_value={'chemical1': '001'})
    def test_to_dataframe(self, mock_chem_map, mock_organism_code, mock_get_allowed_chemicals, mock_allowed_organisms):
        harvester = make_harvester()
        dataframes = harvester.to_dataframe()
        sample_dataframe = dataframes[0]
        general_dataframe = dataframes[1]

        for col in SAMPLE_SHEET_COLUMNS:
            self.assertIn(col, sample_dataframe.columns)
        self.assertEqual(26, len(sample_dataframe.index))
        self.assertEqual(len(sample_dataframe.iloc[0]), len(SAMPLE_SHEET_COLUMNS))

        for col in GENERAL_SHEET_COLUMNS:
            self.assertIn(col, general_dataframe.columns)

    @patch('ptmd.model.inputs2dataframes.get_organism_code', return_value="X")
    @patch('ptmd.model.inputs2dataframes.get_chemical_code_mapping', return_value={'chemical1': '001'})
    def test_save_dataframe(self, mock_chem_map, mock_org_code, mock_get_allowed_chemicals, mock_allowed_organisms):
        output_path = path.join(HERE, '..', 'data', 'excel', 'test.xlsx')
        harvester = make_harvester()
        file_path = harvester.save_file(output_path)
        self.assertIsNotNone(file_path)

    @patch('ptmd.model.inputs2dataframes.get_organism_code', return_value="X")
    @patch('ptmd.model.inputs2dataframes.get_chemical_code_mapping', return_value={'chemical1': '001'})
    def test_delete_file(self, mock_chem_map, mock_organism_code, mock_get_allowed_chemicals, mock_allowed_organisms):
        output_path = path.join(HERE, '..', 'data', 'excel', 'temp.xlsx')
        harvester = make_harvester()
        file_path = harvester.save_file(output_path)
        self.assertIsNotNone(file_path)
        harvester.delete_file()
        self.assertFalse(path.exists(output_path))

        with self.assertRaises(FileNotFoundError) as context:
            harvester = make_harvester()
            harvester.delete_file()
        self.assertEqual('This input was not saved yet.', str(context.exception))


def make_harvester():
    exposure_conditions = [ExposureCondition(**EXPOSURE_CONDITIONS[0])]
    return Inputs2Dataframes(partner=PARTNER,
                             organism=ORGANISM,
                             exposure_conditions=exposure_conditions,
                             exposure_batch=EXPOSURE_BATCH,
                             replicate4exposure=REPLICATES_EXPOSURE,
                             replicate4control=REPLICATES_CONTROL,
                             replicate_blank=REPLICATES_BLANK,
                             start_date=START_DATE, vehicle=VEHICLE,
                             end_date=END_DATE, timepoints=TIMEPOINTS)
