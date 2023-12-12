from unittest import TestCase
from unittest.mock import patch

from ptmd.api import app
from ptmd.database.models import Sample, Organisation, File, Organism, Chemical
from ptmd.api.queries.samples.core import SampleGenerator, save_samples


HEADERS = {'Content-Type': 'application/json', 'Authorization': 'Bearer 123'}
SAMPLES = [
    {
        "precisiontox_short_identifier": "A",
        "compound_name": "test",
    },
    {
        "precisiontox_short_identifier": "B",
        "compound_name": "CONTROL_test1",
    }
]


class MockSample:
    def __init__(self):
        self.sample_id = "A"
        self.file_id = 1
        self.data = {"test": "test"}


@patch('ptmd.api.queries.utils.get_current_user')
@patch('ptmd.api.queries.utils.verify_jwt_in_request')
@patch('flask_jwt_extended.view_decorators.verify_jwt_in_request')
class TestSamples(TestCase):

    def test_get_sample_error_404(self, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        with patch('ptmd.api.queries.samples.core.Sample') as mock_sample:
            mock_sample.query.filter().first.return_value = None
            mock_user().id = 1
            mock_user().role = 'admin'
            with app.test_client() as client:
                response = client.get('/api/samples/1', headers=HEADERS)
                self.assertEqual(response.json, {'message': 'Sample 1 not found.'})
                self.assertEqual(response.status_code, 404)

    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.chemical.get_current_user')
    @patch('ptmd.database.models.sample.get_current_user')
    def test_get_sample_success(self, mock_get_current_user, mock_chemical_user, mock_organisation,
                                mock_organism, mock_chemical,
                                mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        organisation = Organisation(name='test', longname='test')
        mock_organisation.query.filter_by().first.return_value = organisation
        file = self.get_file(organisation)
        sample = Sample(sample_id="ABC", data={'test': 'test'}, file_id=1)
        sample.file = file

        expected = {
            'batch': 'test',
            'google_file': 'test',
            'organisation': 'test',
            'organism': 'test',
            'test': 'test',
            'vehicle': {
                'cas': None,
                'chemical_id': 1,
                'common_name': 'test',
                'formula': None,
                'ptx_code': 'PTXNone'
            }
        }
        with patch('ptmd.api.queries.samples.core.Sample') as mock_sample:
            mock_sample.query.filter().first.return_value = sample
            mock_user().id = 1
            mock_chemical_user().role = 'admin'
            mock_chemical_user().id = 1
            mock_user().role = 'admin'
            with app.test_client() as client:
                response = client.get('/api/samples/1', headers=HEADERS)
                self.assertEqual(response.json, {'sample': expected})
                self.assertEqual(response.status_code, 200)

    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.chemical.get_current_user')
    @patch('ptmd.database.models.sample.get_current_user')
    def test_get_sample_success_public(self, mock_get_current_user, mock_chemical_user, mock_organisation,
                                       mock_organism, mock_chemical,
                                       mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        organisation = Organisation(name='test', longname='test')
        mock_organisation.query.filter_by().first.return_value = organisation
        mock_get_current_user.return_value = None
        file = self.get_file(organisation)
        sample_data = {
            'replicate': 1, 'dose_code': 'A',
            'compound': {'ptx_code': 'PTXNone', 'common_name': 'test'},
            'timepoint_(hours)': 1
        }
        sample = Sample(sample_id="ABC", data=sample_data, file_id=1)
        sample.file = file
        expected = {
            'batch': 'test',
            'compound': {'name': 'test', 'ptox_id': 'PTXNone'},
            'dose': 'A',
            'ptox_id': 'ABC',
            'replicate': 1,
            'timepoint_hours': 1,
            'vehicle': 'test'
        }
        with patch('ptmd.api.queries.samples.core.Sample') as mock_sample:
            mock_sample.query.filter().first.return_value = sample
            mock_user().id = 1
            mock_chemical_user().role = 'admin'
            mock_chemical_user().id = 1
            mock_user().role = 'admin'
            with app.test_client() as client:
                response = client.get('/api/samples/1', headers=HEADERS)
                self.assertEqual(response.json, {'sample': expected})
                self.assertEqual(response.status_code, 200)

    def test_get_samples(self, mock_jwt_verify_flask, mock_jwt_verify_utils, mock_user):
        class MockQuery:
            def __init__(self):
                self.items = []
                self.has_next = False
                self.has_prev = False
                self.pages = 1
                self.total = 0

        with patch('ptmd.api.queries.samples.core.Sample') as mock_sample:
            mock_sample.query.paginate.return_value = MockQuery()
            mock_user().id = 1
            mock_user().role = 'admin'
            with app.test_client() as client:
                response = client.get('/api/samples', headers=HEADERS)
                self.assertEqual(response.json['samples'], [])
                self.assertEqual(response.json['pagination'], {
                    'current_page': 1,
                    'next_page': None,
                    'pages': 1,
                    'per_page': 10,
                    'previous_previous': None,
                    'total': 0
                })
                self.assertEqual(response.status_code, 200)

    @staticmethod
    def get_file(organisation):
        file = File(gdrive_id='test', name='test', batch='test', replicates=1, controls=1, blanks=1,
                    organisation_name="org", user_id=1, organism_name='test', vehicle_name="vehicle",
                    start_date='2021-01-01', end_date='2021-01-01')
        file.organism = Organism(ptox_biosystem_name='test', scientific_name='test', ptox_biosystem_code='test')
        file.organisation = organisation
        file.vehicle = Chemical(common_name='test', chemical_id=1)
        return file


class TestSampleGenerator(TestCase):

    @patch('ptmd.api.queries.samples.core.jsonify', return_value="Not found.")
    def test_sample_generator_error_404(self, mock_jsonify):
        with patch('ptmd.api.queries.samples.core.File') as mock_file:
            mock_file.query.filter().first.return_value = None
            sample_generator = SampleGenerator(file_id=1)
            self.assertEqual(sample_generator.response, ('Not found.', 404))

    @patch('ptmd.api.queries.samples.core.jsonify', return_value="Not allowed.")
    @patch('ptmd.api.queries.samples.core.get_current_user')
    def test_sample_generator_error_403(self, mock_user, mock_jsonify):
        class MockFile:
            def __init__(self):
                self.author = "user"

        mock_user().role = 'user'
        with patch('ptmd.api.queries.samples.core.File') as mock_file:
            mock_file.query.filter().first.return_value = MockFile()
            sample_generator = SampleGenerator(file_id=1)
            self.assertEqual(sample_generator.response, ('Not allowed.', 403))

    @patch('ptmd.api.queries.samples.core.jsonify', return_value="Not valid.")
    @patch('ptmd.api.queries.samples.core.get_current_user')
    def test_sample_generator_error_400(self, mock_user, mock_jsonify):
        mock_user().role = 'admin'

        class MockFile:
            def __init__(self):
                self.author = mock_user
                self.validated = 'No'

        with patch('ptmd.api.queries.samples.core.File') as mock_file:
            mock_file.query.filter().first.return_value = MockFile()
            sample_generator = SampleGenerator(file_id=1)
            self.assertEqual(sample_generator.response, ('Not valid.', 400))

    @patch('ptmd.api.queries.samples.core.get_current_user')
    def test_sample_generator_constructor_success(self, mock_user):
        mock_user().role = 'admin'
        sample_generator, mock_file = self.make_generator(mock_user)
        self.assertEqual(sample_generator.file, mock_file.query.filter().first.return_value)
        self.assertIn("test", sample_generator.filename)
        self.assertIn(".xlsx", sample_generator.filename)
        self.assertNotIn("test.xlsx", sample_generator.filename)

    @patch('ptmd.api.queries.samples.core.get_current_user')
    @patch('ptmd.api.queries.samples.core.session')
    @patch('ptmd.api.queries.samples.core.remove')
    @patch('ptmd.api.queries.samples.core.SampleGenerator.get_data', return_value=({"exposure_info": SAMPLES}, "test"))
    @patch('ptmd.api.queries.samples.core.Chemical')
    @patch('ptmd.api.queries.samples.core.Sample')
    def test_generate_samples(self, mock_sample, mock_chem, mock_get_data, mock_rm, mock_session, mock_user):
        mock_chem.query.filter().first.return_value = None
        mock_sample.query.filter().first.return_value = None
        mock_sample.return_value = MockSample()
        sample_generator, _ = self.make_generator(mock_user)
        samples = sample_generator.generate_samples()
        self.assertEqual(samples, ['A', 'A'])
        mock_session.commit.assert_called_once()
        mock_rm.assert_called_once()
        mock_get_data.assert_called_once()
        self.assertEqual(mock_session.add.call_count, 2)

    @patch('ptmd.api.queries.samples.core.get_current_user')
    @patch('ptmd.api.queries.samples.core.session')
    @patch('ptmd.api.queries.samples.core.remove')
    @patch('ptmd.api.queries.samples.core.SampleGenerator.get_data', return_value=({"exposure_info": SAMPLES}, "test"))
    @patch('ptmd.api.queries.samples.core.Chemical')
    @patch('ptmd.api.queries.samples.core.Sample')
    def test_generate_samples_existing(self, mock_sample, mock_chem, mock_get_data, mock_rm, mock_session, mock_user):
        mocked_sample = MockSample()
        mock_chem.query.filter().first.return_value = None
        mock_sample.query.filter().first.return_value = mocked_sample
        mock_sample.return_value = mocked_sample
        sample_generator, _ = self.make_generator(mock_user)
        samples = sample_generator.generate_samples()
        self.assertEqual(samples, ['A', 'A'])
        mock_session.commit.assert_called_once()
        mock_rm.assert_called_once()
        mock_get_data.assert_called_once()
        self.assertEqual(mock_session.add.call_count, 0)

    @patch('ptmd.api.queries.samples.core.GoogleDriveConnector')
    @patch('ptmd.api.queries.samples.core.ExcelFile')
    @patch('ptmd.api.queries.samples.core.File')
    @patch('ptmd.api.queries.samples.core.get_current_user')
    def test_get_data(self, mock_user, mock_file, mock_excel, mock_drive):
        class MockFile:
            def __init__(self):
                self.validated = 'success'
                self.gdrive_id = '123'
                self.author = "user"
                self.name = "test.xlsx"

        mock_user().role = 'admin'
        mock_file.query.filter().first.return_value = MockFile()

        mock_drive().download_file.return_value = "filepath"
        mock_excel().parse().replace().replace().to_dict.return_value = []
        mock_excel().parse().replace().to_dict().__getitem__.return_value = []

        generator = SampleGenerator(file_id=1)
        generator.filename = "test.xlsx"
        generator.file = MockFile()
        data = generator.get_data()
        self.assertEqual(data, ({"exposure_info": [], "general_info": []}, "filepath"))

    @patch('ptmd.api.queries.utils.verify_jwt_in_request')
    @patch('ptmd.api.queries.utils.get_current_user')
    @patch('ptmd.api.queries.samples.core.SampleGenerator')
    def test_save_samples(self, mock_generator, mock_user, mock_role):
        mock_user().role = 'admin'
        response = {}, 200
        mock_generator().response = response
        samples = save_samples(1)
        self.assertEqual(samples, response)

        with patch('ptmd.api.queries.samples.core.jsonify') as mock_jsonify:
            mock_jsonify.return_value = "Hello"
            mock_generator().generate_samples.return_value = ["A", "B"]
            del mock_generator().response
            samples = save_samples(1)
            self.assertEqual(samples, ('Hello', 200))

    @staticmethod
    def make_generator(mocked_user):
        mocked_user().role = 'admin'

        class MockFile:
            def __init__(self):
                self.author = mocked_user
                self.validated = 'success'
                self.name = 'test.xlsx'

        with patch('ptmd.api.queries.samples.core.File') as mocked_file:
            mocked_file.query.filter().first.return_value = MockFile()
            generator = SampleGenerator(file_id=1)
            generator.compounds = {"test": {"common_name": "test"}}
            return generator, mocked_file
