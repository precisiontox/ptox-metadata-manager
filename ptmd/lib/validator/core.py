""" The core of the validator.
"""
from __future__ import annotations

from typing import Generator
from os import remove

from json import loads
from jsonschema import Draft4Validator as JSONValidator
from numpy import nan
from pandas import DataFrame, ExcelFile

from ptmd.const import EXPOSURE_INFORMATION_SCHEMA_FILEPATH, PTX_ID_LABEL
from ptmd.config import session
from ptmd.database import File
from ptmd.lib.gdrive import GoogleDriveConnector
from .validate_identifier import validate_identifier


class ExcelValidator:
    """ The core of the validator.

    :param file_id: The file id to validate.
    """

    def __init__(self, file_id: int | str) -> None:
        """ The validator constructor. """
        self.report: dict = {'valid': True, 'errors': {}}
        self.current_record: dict = {'data': {}, 'label': ''}
        self.general_info: dict = {}
        self.exposure_data: list[dict] = []
        self.identifiers: list[str] = []
        self.vertical_validation_data: dict = {}
        self.__schema: dict = {}
        self.file_id: int | str = file_id
        self.file: dict = {}
        self.filepath: str = ''

    def validate(self) -> None:
        """ Validates the file. """
        if isinstance(self.file_id, int):
            self.file = self.__get_file_from_database(self.file_id)
            filepath: str | None = self.download_file()
            if filepath:
                self.filepath = filepath
            self.validate_file()
            self.__update_file_record()

            remove(self.filepath)

    @staticmethod
    def __get_file_from_database(file_id: int) -> dict[str, str]:
        """ Get the file id from the database.

        :param file_id: The file id to get.
        :return: The file id.
        """
        file: File = File.query.filter(File.file_id == file_id).first()
        if not file:
            raise ValueError(f"File with ID {file_id} does not exist.")
        return dict(file)

    def download_file(self) -> str | None:
        """ Download the file from Google Drive.

        :return: the downloaded file path.
        """
        gdrive: GoogleDriveConnector = GoogleDriveConnector()
        return gdrive.download_file(self.file['gdrive_id'], self.file['name'])

    def __load_data(self) -> None:
        """ Load the dataframe and schema in memory.
        """
        file_handler: ExcelFile = ExcelFile(self.filepath, engine='openpyxl')
        exposure_df: DataFrame = file_handler.parse("Exposure information")
        general_df: DataFrame = file_handler.parse("General Information")
        self.exposure_data = exposure_df.replace({nan: None}).to_dict(orient='records')
        self.general_info = general_df.replace({nan: None}).to_dict(orient='records')[0]
        timepoints: str = self.general_info['timepoints'].strip('[]').split(', ')
        self.general_info['timepoints'] = list(map(lambda x: int(x), timepoints))
        with open(EXPOSURE_INFORMATION_SCHEMA_FILEPATH, 'r') as f:
            self.__schema = loads(f.read())

    def validate_file(self) -> None:
        """ Validates the file.
        """
        self.__load_data()
        validator: JSONValidator = JSONValidator(self.__schema)
        self.report['valid'] = True
        graph: VerticalValidator = VerticalValidator(self.general_info, self)

        for record_index, record in enumerate(self.exposure_data):
            ptx_id: str = record[PTX_ID_LABEL]
            label: str = f"Record at line {record_index + 2} ({ptx_id})"
            errors: Generator = validator.iter_errors(record)
            self.current_record = {'data': record, 'label': label}

            for error in errors:
                message: str = "This field is required." if "None is not of type" in error.message else error.message
                field: str = error.message.split("'")[1] if not error.path else error.path[0]
                self.add_error(label, message, field)

            graph.add_node(self.current_record)

            validate_identifier(excel_validator=self, record_index=record_index)

        graph.validate()

    def add_error(self, label: str, message: str, field: str) -> None:
        """ Adds an error to the report.

        :param label: The label of the record.
        :param message: The error message.
        :param field: The field concerned by the error.
        :return: None
        """
        self.report['valid'] = False
        if label not in self.report['errors']:
            self.report['errors'][label] = []
        self.report['errors'][label].append({'message': message, 'field_concerned': field})

    def __update_file_record(self) -> None:
        """ Updates the 'validated' property of the file record in the database.
        'success': if the validation was successful.
        'failed': if the validation was not successful.
        Default is 'No' before the first validation.

        :return: None
        """
        File.query.filter(File.file_id == self.file['file_id']).update(
            {'validated': 'success' if self.report['valid'] else 'failed'})
        session.commit()
        session.close()


class ExternalExcelValidator(ExcelValidator):
    """ Variation of the ExcelValidator for external files that doesn't use the database.

    :param file_id: The file id to validate.
    """

    def __init__(self, file_id: str) -> None:
        """ The validator constructor. """
        super().__init__(file_id)

    def validate(self) -> None:
        """ Validates the file. """
        file: str | None = self.download_file()
        if file:
            self.filepath = file
        self.validate_file()
        remove(self.filepath)

    def download_file(self) -> str | None:
        """ Download the file from Google Drive.

        :return: the downloaded file path.
        """
        gdrive: GoogleDriveConnector = GoogleDriveConnector()
        file: dict = gdrive.google_drive.CreateFile({'id': self.file_id})
        return gdrive.download_file(self.file_id, file['title'])


class VerticalValidator:
    """ Validate the study design of the exposure information using the general information sheet.

    :param definitions: The general information sheet.
    :param validator: The ExcelValidator instance.
    """

    def __init__(self, definitions: dict, validator: ExcelValidator) -> None:
        """ The validator constructor. """
        self.controls_keys: list[str] = ['CONTROL (DMSO)', 'CONTROL (WATER)']
        self.validator: ExcelValidator = validator
        self.timepoints: list = definitions['timepoints']
        self.replicates: int = definitions['replicates']
        self.blanks: int = definitions['blanks']
        self.controls: int = definitions['control']
        self.vehicle: str = definitions['compound_vehicle']

        self.compounds: dict = {}
        self.extraction_blanks: int = 0

        self.box_positions: list[str] = []
        self.collection_order: list[int] = []

    def add_node(self, node: dict) -> None:
        """ Add the node and validates it.

        :param node: The node to add.
        :return: None
        """
        message: str
        label: str = node['label']
        compound_name: str = node['data'].get('compound_name', None)
        replicate: int = node['data'].get('replicate', None)
        timepoint: int = node['data'].get('timepoint_(hours)', None)
        dose: int = node['data'].get('dose_code', None)
        box_position: str = (f"{node['data'].get('box_id')}"
                             f"_{node['data'].get('box_row')}"
                             f"_{node['data'].get('box_column')}")
        collection_order: int = node['data'].get('collection_order')

        if compound_name:
            if box_position in self.box_positions:
                message = f"Box position {box_position} is already used."
                self.validator.add_error(label, message, 'box_position')
            else:
                self.box_positions.append(box_position)

            if collection_order in self.collection_order:
                message = f"Collection order {collection_order} is already used."
                self.validator.add_error(label, message, 'collection_order')
            else:
                self.collection_order.append(collection_order)

            if compound_name not in self.controls_keys and replicate > self.replicates:
                message = f"Replicate {replicate} is greater than the number of replicates {self.replicates}."
                self.validator.add_error(label, message, 'replicate')

            if timepoint not in self.timepoints and compound_name != 'EXTRACTION BLANK':
                message = f"Timepoint {timepoint} is not in the list of timepoints {self.timepoints}."
                self.validator.add_error(label, message, 'timepoint_(hours)')

            if compound_name == 'EXTRACTION BLANK':
                self.extraction_blanks += 1
                if timepoint != 0:
                    message = "Extraction blank must have a timepoint of 0."
                    self.validator.add_error(label, message, 'timepoint_(hours)')

            if compound_name in self.controls_keys:
                if dose != 0:
                    message = "Controls must have a dose of 0."
                    self.validator.add_error(label, message, 'dose_code')
                if replicate > self.controls:
                    message = f"Control {replicate} is greater than the number of controls {self.controls}."
                    self.validator.add_error(label, message, 'replicate')

            if compound_name not in self.compounds:
                self.compounds[compound_name] = {
                    'replicates': {},
                    'timepoints': {}
                }

            if timepoint not in self.compounds[compound_name]['replicates']:
                self.compounds[compound_name]['replicates'][timepoint] = 0
            if replicate not in self.compounds[compound_name]['timepoints']:
                self.compounds[compound_name]['timepoints'][replicate] = 0

            self.compounds[compound_name]['replicates'][timepoint] += 1
            self.compounds[compound_name]['timepoints'][replicate] += 1

    def validate(self) -> None:
        """ Validates the study design after all nodes have been added

        :return: None
        """
        if self.extraction_blanks != self.blanks:
            message = f"The number of extraction blanks should be {self.blanks} but is {self.extraction_blanks}"
            self.validator.add_error('Extraction blanks', message, 'compound_name')

        for compound_name, compound_val in self.compounds.items():
            if compound_name == 'EXTRACTION BLANK':
                break

            for timepoint in compound_val['replicates']:
                if timepoint in self.timepoints:
                    replicate: int = compound_val['replicates'][timepoint]
                    index: int = self.timepoints.index(timepoint) + 1
                    if replicate < self.replicates:
                        message = f"Replicate {index} is missing {self.replicates - replicate } timespoints(s)."
                        self.validator.add_error(compound_name, message, 'timepoints')
                    elif replicate > self.replicates:
                        message = f"Replicate {index} has too many timepoints."
                        self.validator.add_error(compound_name, message, 'timepoints')

            for replicate in compound_val['timepoints']:
                timepoint = compound_val['timepoints'][replicate]
                if timepoint > len(self.timepoints):
                    message = f"Timepoint {replicate} has greater number of replicates {timepoint} " \
                              f"than expected ({self.replicates})."
                    self.validator.add_error(compound_name, message, 'replicates')
                elif timepoint < len(self.timepoints):
                    message = f"Timepoint {replicate} is missing {len(self.timepoints) - timepoint} replicate(s)."
                    self.validator.add_error(compound_name, message, 'replicates')
