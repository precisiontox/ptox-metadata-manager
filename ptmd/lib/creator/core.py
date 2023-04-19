""" The core module of the creator package. Takes the user input, validates them and creates the dataframes.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from typing import Generator
from os import remove
from datetime import datetime

from pandas import DataFrame
from jsonschema import Draft202012Validator as JSONValidator, ValidationError, RefResolver
from dateutil.parser import parse as parse_date

from ptmd.const import INPUT_SCHEMA, EXPOSURE_SCHEMA
from ptmd.database import get_allowed_organisms, get_organism_code, get_chemical_code_mapping
from ptmd.lib.creator.dataframes import build_general_dataframe, build_sample_dataframe
from ptmd.lib.excel import save_to_excel


class DataframeCreator:
    """ Class to create the dataframes from the user input.

    :param user_input: the user input
    """

    def __init__(self, user_input: dict) -> None:
        """ Constructor of the class. """
        self.__general_information_schema: dict = INPUT_SCHEMA
        self.__exposure_information_schema: dict = EXPOSURE_SCHEMA
        self.__user_input: dict = user_input

        self.validate()

        self.partner: str = user_input['partner']
        self.organism: str = user_input['organism']
        self.exposure_batch: str = user_input['exposure_batch']
        self.replicates4exposure: int = user_input['replicates4exposure']
        self.replicates4control: int = user_input['replicates4control']
        self.replicates_blank: int = user_input['replicates_blank']
        self.start_date: datetime = parse_date(user_input['start_date'])
        self.end_date: datetime = parse_date(user_input['end_date'])
        self.timepoints: list[int] = user_input['timepoints']
        self.vehicle: str = user_input['vehicle']
        self.exposure_conditions: list[dict] = user_input['exposure']
        self.file_path: str = ''

    def validate(self) -> None:
        """ Validates the user input against the JSON SChema

        :return: None
        """
        mapping: dict = {
            self.__general_information_schema['$id']: self.__general_information_schema,
            self.__exposure_information_schema['$id']: self.__exposure_information_schema
        }
        resolver: RefResolver = RefResolver(store=mapping,
                                            base_uri='file:///',
                                            referrer=self.__general_information_schema)
        validator: JSONValidator = JSONValidator(self.__general_information_schema, resolver=resolver)
        errors: Generator = validator.iter_errors(self.__user_input)
        for error in errors:
            message: str = f"'{error.path[0]}' value {error.message}" if error.path else error.message
            raise ValidationError(message)

    def get_array_of_unique_chemicals(self) -> list[str]:
        """ Get an array of unique chemicals from the exposure conditions.

        :return: The array of unique chemicals names.
        """
        array_of_unique_chemicals: list[str] = []
        for exposure_condition in self.exposure_conditions:
            for chemical in exposure_condition['chemicals']:
                if chemical not in array_of_unique_chemicals:
                    array_of_unique_chemicals.append(chemical)
        return array_of_unique_chemicals

    def to_dataframe(self) -> tuple[DataFrame, DataFrame]:
        """ Convert the object to a pandas DataFrame.

        :return: The pandas DataFrame.
        """
        if self.organism not in get_allowed_organisms():
            raise ValueError(f"Organism {self.organism} not found in the database.")
        chemical_map: dict = get_chemical_code_mapping(self.get_array_of_unique_chemicals())
        organism_code: str = get_organism_code(self.organism)
        sample_dataframe: DataFrame = build_sample_dataframe(harvester=self,
                                                             organism_code=organism_code,
                                                             chemicals_mapping=chemical_map)

        return sample_dataframe, build_general_dataframe(harvester=self)

    def save_file(self, path: str) -> str:
        """ Save the sample sheet to a file.

        :param path: The path to the file.
        :return: The path to the file the sample sheet was saved to.
        """
        self.file_path = save_to_excel(dataframes=self.to_dataframe(), path=path)
        return path

    def delete_file(self) -> None:
        """ Delete the sample sheet file. """
        if not self.file_path:
            raise FileNotFoundError('This input was not saved yet.')
        remove(self.file_path)
