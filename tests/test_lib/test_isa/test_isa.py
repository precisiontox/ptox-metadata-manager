from unittest import TestCase
from unittest.mock import patch

from isatools.model import Investigation

from ptmd.lib.isa import convert_file_to_isa
from ptmd.database.models import File, Organism, Sample, Organisation, Chemical


SAMPLE_DATA = {"sampleid_label": "DAD100LA1", "shipment_identifier": "2023-06-29",
               "Label_tube_/_identifier": "DAD100LA1", "box_id": "Box1", "exposure_route": "medium",
               "operator": "MJones", "quantity_dead_during_exposure": 0, "amount_replaced_before_collection": 0,
               "collection_order": 1, "box_row": "A", "box_column": 1, "mass_including_tube_(mg)": None,
               "mass_excluding_tube_(mg)": None, "observations_notes": "Note", "replicate": 1,
               "dose_code": "BMD10", "timepoint_level": "TP1", "timepoint_(hours)": 4,
               "precisiontox_short_identifier": "DAD100LA1",
               "compound": {"common_name": "Cytosine arabinoside", "cas": "147-94-4", "formula": "C9H13N3O5",
                            "ptx_code": "PTX100", "chemical_id": 102}}
BLANK_SAMPLE_DATA = {"sampleid_label": "DAD998ZS2", "shipment_identifier": "2023-06-29",
                     "Label_tube_/_identifier": "DAD998ZS2", "box_id": "Box1",
                     "exposure_route": "medium", "operator": "MJones", "quantity_dead_during_exposure": 0,
                     "amount_replaced_before_collection": 0, "collection_order": 49, "box_row": "F",
                     "box_column": 5, "mass_including_tube_(mg)": None, "mass_excluding_tube_(mg)": None,
                     "observations_notes": None, "replicate": 2, "dose_code": "0", "timepoint_level": "TP0",
                     "timepoint_(hours)": 0, "precisiontox_short_identifier": "DAD998ZS2",
                     "compound": "EXTRACTION BLANK"}
CONTROL_SAMPLE_DATA = {"sampleid_label": "DAD997ZA4", "shipment_identifier": "2023-06-29",
                       "Label_tube_/_identifier": "DAD997ZA4", "box_id": "Box1", "exposure_route": "medium",
                       "operator": "MJones", "quantity_dead_during_exposure": 0, "amount_replaced_before_collection": 0,
                       "collection_order": 45, "box_row": "F", "box_column": 1, "mass_including_tube_(mg)": None,
                       "mass_excluding_tube_(mg)": None, "observations_notes": None, "replicate": 4, "dose_code": 0,
                       "timepoint_level": "TP1", "timepoint_(hours)": 4, "precisiontox_short_identifier": "DAD997ZA4",
                       "compound": "CONTROL (Water)"}


class TestIsa(TestCase):

    def test_converter_errors(self):
        with patch('ptmd.lib.isa.File') as mock_file:
            mock_file.query.filter().first.return_value = None
            with self.assertRaises(FileNotFoundError) as context:
                convert_file_to_isa(1)
            self.assertEqual(str(context.exception), 'File with id 1 not found')

            mock_file.query.filter().first.return_value = mock_file
            mock_file.received = False
            with self.assertRaises(ValueError) as context:
                convert_file_to_isa(1)
            self.assertEqual(str(context.exception), 'File with id 1 has not been received yet')

    @patch('ptmd.lib.isa.File')
    @patch('ptmd.database.models.file.Chemical')
    @patch('ptmd.database.models.file.Organism')
    @patch('ptmd.database.models.file.Organisation')
    @patch('ptmd.database.models.chemical.get_current_user', return_value=None)
    @patch('ptmd.database.models.sample.get_current_user')
    def test_converter_success(self, mock_get_current_user_sample, mock_get_current_user_chemical,
                               mock_organisation, mock_organism, mock_chemical, mock_file):
        mock_organisation.query.filter_by().first.return_value.organisation_id = 1
        mock_organism.query.filter_by().first.return_value.organism_id = 1
        mock_chemical.query.filter_by().first.return_value.chemical_id = 1
        organism = Organism(ptox_biosystem_name='Danio_rerio', scientific_name='Danio_rerio', ptox_biosystem_code='AC')
        organisation = Organisation(longname='org', name='org')
        chemical = Chemical(common_name='foo', cas='bar', formula='AC', ptx_code=1)
        sample = Sample(sample_id="ABC", data=SAMPLE_DATA, file_id=1)
        blank_sample = Sample(sample_id="BLANK_", data=BLANK_SAMPLE_DATA, file_id=1)
        control_sample = Sample(sample_id="CONTROL_", data=CONTROL_SAMPLE_DATA, file_id=1)
        file = File(
            gdrive_id='foo',
            name='bar',
            batch='AC',
            replicates=1,
            controls=1,
            blanks=1,
            organisation_name='org',
            user_id=1,
            organism_name='org',
            vehicle_name='water',
            doses=[],
            chemicals=[],
            timepoints=[],
            start_date='2021-01-01',
            end_date='2021-01-01'
        )
        file.received = True
        file.organism = organism
        file.samples = [sample, blank_sample, control_sample]
        file.organisation = organisation
        file.vehicle = chemical
        mock_file.query.filter().first.return_value = file

        isa = convert_file_to_isa(1)[0]
        investigation = Investigation()
        investigation.from_dict(isa)
        self.assertIsInstance(investigation, Investigation)

        another_organism = Organism(ptox_biosystem_name='Drosophila_melanogaster_male',
                                    scientific_name='Drosophila_melanogaster_male', ptox_biosystem_code='GTT')
        file.organism = another_organism
        isa = convert_file_to_isa(1)[0]
        investigation = Investigation()
        investigation.from_dict(isa)
        self.assertIsInstance(investigation, Investigation)

        new_isa = Investigation()
        new_isa.from_dict(investigation.to_dict())
        self.assertEqual(investigation, new_isa)
