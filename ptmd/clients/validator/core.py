""" The core of the validator.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from typing import Generator
from os import remove

from json import loads
from jsonschema import Draft202012Validator as JSONValidator
from numpy import nan
from pandas import DataFrame, ExcelFile
from sqlalchemy.orm import Session

from ptmd.utils import get_session
from ptmd.const import EXPOSURE_INFORMATION_SCHEMA_FILEPATH
from ptmd.database import File
from ptmd.clients.gdrive import GoogleDriveConnector
from .const import PTX_ID_LABEL
from .validate_identifier import validate_identifier


class ExcelValidator:
    """ The core of the validator.

    :param file_id: The file id to validate.
    """

    def __init__(self, file_id: int | str):
        """ The validator constructor. """
        self.report: dict = {'valid': True, 'errors': {}}
        self.current_record: dict = {'data': {}, 'label': ''}
        self.general_info: dict = {}
        self.exposure_data: list[dict] = []
        self.identifiers: list[str] = []
        self.__schema: dict = {}
        self.file_id: int | str = file_id
        self.session: Session | None = None
        self.file: dict = {}
        self.filepath: str = ''

    def validate(self):
        """ Validates the file. """
        self.session = get_session()
        self.file = self.__get_file_from_database(self.file_id)
        self.filepath = self.download_file()
        self.validate_file()
        self.__update_file_record()

        remove(self.filepath)
        self.session.close()

    def __get_file_from_database(self, file_id: int) -> dict[str, str]:
        """ Get the file id from the database.

        :param file_id: The file id to get.
        :return: The file id.
        """
        file: File = self.session.query(File).filter(File.file_id == file_id).first()
        if not file:
            raise ValueError(f"File with ID {file_id} does not exist.")
        return dict(file)

    def download_file(self) -> str:
        """ Download the file from Google Drive.

        :return: the downloaded file path.
        """
        gdrive: GoogleDriveConnector = GoogleDriveConnector()
        filepath: str = gdrive.download_file(self.file['gdrive_id'], self.file['name'])
        return filepath

    def __load_data(self) -> None:
        """ Load the dataframe and schema in memory.
        """
        file_handler: ExcelFile = ExcelFile(self.filepath, engine='openpyxl')
        exposure_df: DataFrame = file_handler.parse("Exposure information")
        general_df: DataFrame = file_handler.parse("General Information")
        self.exposure_data = exposure_df.replace({nan: None}).to_dict(orient='records')
        self.general_info = general_df.replace({nan: None}).to_dict(orient='records')[0]
        with open(EXPOSURE_INFORMATION_SCHEMA_FILEPATH, 'r') as f:
            self.__schema = loads(f.read())

    def validate_file(self) -> None:
        """ Validates the file.
        """
        self.__load_data()
        validator: JSONValidator = JSONValidator(self.__schema)
        self.report['valid'] = True

        for record_index, record in enumerate(self.exposure_data):
            ptx_id: str = record[PTX_ID_LABEL]
            label: str = f"Record at line {record_index + 2} ({ptx_id})"
            errors: Generator = validator.iter_errors(record)
            self.current_record = {'data': record, 'label': label}

            for error in errors:
                self.report['valid'] = False
                message: str = error.message
                if "None is not of type" in message:
                    message = "This field is required."
                self.add_error(label, message, error.path[0])
            validate_identifier(excel_validator=self, record_index=record_index)

    def add_error(self, label, message, field):
        """ Adds an error to the report.

        :param label: The label of the record.
        :param message: The error message.
        :param field: The field concerned by the error.
        :return: None
        """
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
        self.session.query(File).filter(File.file_id == self.file['file_id']).update(
            {'validated': 'success' if self.report['valid'] else 'failed'})
        self.session.commit()


class ExternalExcelValidator(ExcelValidator):
    """ Variation of the ExcelValidator for external files that doesn't use the database.

    :param file_id: The file id to validate.
    """

    def __init__(self, file_id: str):
        super().__init__(file_id)

    def validate(self):
        self.filepath = self.download_file()
        self.validate_file()
        remove(self.filepath)

    def download_file(self) -> str:
        """ Download the file from Google Drive.

        :return: the downloaded file path.
        """
        gdrive: GoogleDriveConnector = GoogleDriveConnector()
        file = gdrive.google_drive.CreateFile({'id': self.file_id})
        filepath: str = gdrive.download_file(self.file_id, file['title'])
        return filepath
