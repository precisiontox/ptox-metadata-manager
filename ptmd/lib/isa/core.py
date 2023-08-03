""" This module contains the core functionality for converting a batch of PTMD data to ISA-Tab format.

@author: D. Batista (Terazus)
"""

from __future__ import annotations

from isatools.model import (
    Sample, Source, Characteristic, Study, Investigation, OntologyAnnotation,
    Protocol, ProtocolParameter, StudyFactor, FactorValue, ParameterValue, Process,
    Comment
)

from ptmd.const import PTX_ID_LABEL
from ptmd.database.models import File
from ptmd.lib.isa.ontologies import (
    ONTOLOGY_SOURCES,
    ORGANISM_OA, ORGANISM_NA_OA,
    DROSOPHILA_OA,
    MALE_OA,
    FEMALE_OA,
    SEX_OA,
    SPECIES,
    HOURS_OA,
    BOX_OA, POSITION_OA,
    REPLICATE_OA,
    DOSE_OA, COMPOUND_OA, TIMEPOINT_OA,
    TREATMENT_OA,
    TREATMENT_PARAMETERS
)


class Batch2ISA:
    """ Class for converting a batch of PTMD data to ISA-Tab format.

    :param file: The file to convert.
    """

    def __init__(self, file: File) -> None:
        """ Converter constructor. """
        self.filename: str = file.name
        self.data: dict = {
            'general_info': dict(file),
            'exposure_info': [dict(sample) for sample in file.samples]
        }
        self.organism_name: str = file.organism.ptox_biosystem_name
        self.protocol_parameters: dict[str, ProtocolParameter] = {}
        self.factors: dict[str, StudyFactor] = {}
        self.create_factors()
        self.blank_source: Source = self.create_blank_source()

    def convert(self) -> list[dict]:
        """ Convert the file to ISA format.

        :return: A list of dictionaries containing the ISA investigations.
        """
        study: Study = Study(
            filename=self.filename,
            sources=[self.blank_source],
            characteristic_categories=[ORGANISM_OA, SEX_OA, REPLICATE_OA, BOX_OA, POSITION_OA]
        )
        self.create_samples(study)
        study.factors = list(self.factors.values())
        investigation: Investigation = Investigation(
            title="Precision Toxicology Investigation",
            ontology_source_references=ONTOLOGY_SOURCES,
            studies=[study]
        )
        return [investigation.to_dict()]

    @staticmethod
    def create_blank_source() -> Source:
        """ Create a blank source.

        :return: A blank source.
        """
        return Source(name="Blank source", characteristics=[Characteristic(category=ORGANISM_OA, value=ORGANISM_NA_OA)])

    @staticmethod
    def create_characteristic(box_id: str, position: str, replicate: int) -> list[Characteristic]:
        """ Create characteristics for a sample.

        :param box_id: The box id of the sample.
        :param position: The position of the sample.
        :param replicate: The replicate of the sample.
        :return: A list of characteristics.
        """
        return [
            Characteristic(category=BOX_OA, value=box_id),
            Characteristic(category=POSITION_OA, value=str(position)),
            Characteristic(category=REPLICATE_OA, value=str(replicate))
        ]

    def create_factors(self) -> None:
        """ Create the factors for the study. """
        dose_factor: StudyFactor = StudyFactor(name="dose", factor_type=DOSE_OA)
        timepoint_factor: StudyFactor = StudyFactor(name="timepoint", factor_type=TIMEPOINT_OA)
        compound_factor: StudyFactor = StudyFactor(name="chemical", factor_type=COMPOUND_OA)
        self.factors = {
            "dose": dose_factor,
            "timepoint": timepoint_factor,
            "compound": compound_factor
        }

    def create_factor_values(self, timepoint: str, dose: str, compound: str | None) -> list[FactorValue]:
        """ Create factor values for a sample.

        :param timepoint: The timepoint of the sample.
        :param dose: The dose of the sample.
        :param compound: The compound of the sample.
        :return: A list of factor values.
        """
        return [
            FactorValue(factor_name=self.factors["timepoint"], value=timepoint, unit=HOURS_OA),
            FactorValue(factor_name=self.factors["dose"], value=dose),
            FactorValue(factor_name=self.factors["compound"], value=compound)
        ]

    def create_parameter_values(self, values: dict) -> list[ParameterValue]:
        """ Create parameter values for a sample.

        :param values: The values of the parameters.
        """
        return [
            ParameterValue(category=self.protocol_parameters["collection_order"],
                           value=str(values['collection_order'])),
            ParameterValue(category=self.protocol_parameters["exposure_batch"], value=values['exposure_batch']),
            ParameterValue(category=self.protocol_parameters["exposure_route"], value=values['exposure_route']),
            ParameterValue(category=self.protocol_parameters["operator"], value=values['operator'])
        ]

    def create_protocol(self) -> Protocol:
        """ Create a protocol for the study.

        :return: A protocol.
        """
        self.create_protocol_parameters(TREATMENT_PARAMETERS)
        treatment_parameters: list[ProtocolParameter] = list(self.protocol_parameters.values())
        return Protocol(name="treatment protocol", protocol_type=TREATMENT_OA, parameters=treatment_parameters)

    def create_protocol_parameters(self, parameter_names: list[str]) -> None:
        """ Create protocol parameters for the study.

        :param parameter_names: The names of the parameters.
        """
        for parameter_name in parameter_names:
            self.protocol_parameters[parameter_name] = ProtocolParameter(parameter_name=parameter_name)

    def create_sample(self, info: dict, study: Study) -> Sample:
        """Create a sample from a dictionary

        :param info: The dictionary containing the sample information.
        :param study: The study to add the sample to.
        :return: A sample.
        """
        compound: str = info['compound'] if type(info['compound']) == str else info['compound']['common_name']
        sample: Sample = Sample(
            id_=f"#sample/{info[PTX_ID_LABEL]}",
            name=info[PTX_ID_LABEL],
            comments=info['comments'],
            derives_from=[info['source']],
            factor_values=self.create_factor_values(
                timepoint=info['timepoint_(hours)'], dose=info['dose_code'], compound=compound
            ),
            characteristics=self.create_characteristic(
                box_id=info['box_id'],
                position=f"(box_row={info['box_row']}, box_column={info['box_column']})",
                replicate=info['replicate']
            ),
        )
        study.samples.append(sample)
        return sample

    def create_samples(self, study: Study) -> None:
        """ Create a sample from a dictionary

        :param study: The study to add the samples to.
        """

        for sample_info in self.data['exposure_info']:
            sample: Sample
            source: Source = self.blank_source

            parameter_values: dict = {
                "collection_order": sample_info['collection_order'],
                "exposure_batch": self.data['general_info']['batch'],
                "exposure_route": sample_info['exposure_route'],
                "operator": sample_info['operator'],
            }
            sample_comments: list[Comment] = []
            if sample_info['observations_notes']:
                sample_comments = [Comment(name="note", value=sample_info['observations_notes'])]

            if type(sample_info['compound']) == str and 'BLANK' in sample_info['compound']:
                sample = self.create_sample({
                    **sample_info,
                    'source': source,
                    'comments': sample_comments,
                    'timepoint_(hours)': '0',
                    'dose_code': '0',
                    'compound_name': None
                }, study)

            elif type(sample_info['compound']) == str and 'CONTROL' in sample_info['compound']:
                source = self.create_source(sample_identifier=sample_info[PTX_ID_LABEL])
                study.sources.append(source)
                sample = self.create_sample({
                    **sample_info,
                    'timepoint_(hours)': '0',
                    'dose_code': '0',
                    'compound_name': sample_info['compound'].replace('CONTROL (', '').replace(')', ''),
                    'source': source,
                    'comments': sample_comments
                }, study)

            else:
                source = self.create_source(sample_identifier=sample_info[PTX_ID_LABEL])
                study.sources.append(source)
                sample = self.create_sample({
                    **sample_info,
                    'source': source,
                    'comments': sample_comments
                }, study)
            protocol: Protocol = self.create_protocol()
            study.protocols.append(protocol)
            process: Process = self.create_treatment_process(
                inputs=[source],
                outputs=[sample],
                protocol=protocol,
                values=parameter_values
            )
            study.process_sequence.append(process)

    def create_source(self, sample_identifier: str) -> Source:
        """ Create a source for a sample.

        :param sample_identifier: The identifier of the sample.
        :return: A source.
        """
        source_name: str = f"Source of sample {sample_identifier}"

        if 'Drosophila_melanogaster' not in self.organism_name:
            return Source(name=source_name, characteristics=[
                Characteristic(category=ORGANISM_OA, value=SPECIES[self.organism_name])
            ])
        sex: OntologyAnnotation = MALE_OA if self.organism_name.split('_')[-1] == 'male' else FEMALE_OA
        return Source(name=source_name, characteristics=[
            Characteristic(category=ORGANISM_OA, value=DROSOPHILA_OA),
            Characteristic(category=SEX_OA, value=sex)
        ])

    def create_treatment_process(self, inputs: list, outputs: list, protocol: Protocol, values: dict) -> Process:
        """ Create a treatment process for a sample.

        :param inputs: The inputs of the process.
        :param outputs: The outputs of the process.
        :param protocol: The protocol of the process.
        :param values: The values of the parameters.
        :return: A process.
        """
        return Process(executes_protocol=protocol,
                       inputs=inputs, outputs=outputs,
                       parameter_values=self.create_parameter_values(values))
