""" This module contains the class for the input of the harvester.

@author: Terazus (D. Batista)
"""
from os import remove
from re import match
from typing import List
from datetime import datetime

from dateutil.parser import parse as parse_date
from pandas import DataFrame

from ptmd.const import (
    ALLOWED_PARTNERS, ALLOWED_EXPOSURE_BATCH, EXPOSURE_BATCH_MAX_LENGTH,
    REPLICATES_EXPOSURE_MIN, REPLICATES_CONTROL_MIN, REPLICATES_BLANK_RANGE,
    TIMEPOINTS_RANGE, ALLOWED_VEHICLES
)
from ptmd.database import get_allowed_organisms, get_organism_code, get_chemical_code_mapping
from ptmd.model.exceptions import InputTypeError, InputValueError, InputMinError, InputRangeError
from ptmd.model.exposure_condition import ExposureCondition
from .interfaces import InputsToDataframes as InputsToDataframesInterface
from .dataframes import build_general_dataframe, build_sample_dataframe
from ptmd.clients.excel import save_to_excel


class Inputs2Dataframes(InputsToDataframesInterface):
    """ A class to represent the input for the harvester and generate the pandas DataFrame and Excel files.

    :param partner: precision tox code of the partner
    :param organism: precision tox code of the organism
    :param exposure_batch:
    :param replicate4exposure: number of replicates for the exposure
    :param replicate4control: number of replicates for the control
    :param replicate_blank: number of blanks
    :param start_date:
    :param end_date:
    :param exposure_conditions: list of chemical names and doses
    :param timepoints: number of timepoints
    :param vehicle: vehicle used in the experiment
    :param timepoint_zero: if the controls should be included at TP0
    """

    def __init__(self,
                 partner: str,
                 organism: str,
                 exposure_batch: str,
                 replicate4exposure: int,
                 replicate4control: int,
                 replicate_blank: int,
                 start_date: str or datetime,
                 end_date: str or datetime,
                 timepoints: int,
                 vehicle: str,
                 timepoint_zero: bool = False,
                 exposure_conditions: List[dict] or List[ExposureCondition] = None) -> None:
        """ The harvester constructor """
        self.allowed_organisms: list[str] = get_allowed_organisms()
        self.partner: str = partner
        self.organism: str = organism
        self.exposure_batch: str = exposure_batch
        self.replicate4exposure: int = replicate4exposure
        self.replicate4control: int = replicate4control
        self.replicate_blank: int = replicate_blank
        self.start_date: str or datetime = start_date
        self.end_date: str or datetime = end_date
        self.timepoints: int = timepoints
        self.vehicle: str = vehicle
        self.timepoint_zero: bool = timepoint_zero
        self.exposure_conditions: list[ExposureCondition] = exposure_conditions if exposure_conditions else []
        self.file_path: str or None = None

    @property
    def partner(self) -> str:
        """ Getter for the partner.

        :return: The partner.
        """
        return self.__partner

    @partner.setter
    def partner(self, value: str) -> None:
        """ Getter for the partner.

        :return: The partner.
        """
        if not isinstance(value, str):
            raise InputTypeError(str, value, 'partner')
        if value not in ALLOWED_PARTNERS:
            raise InputValueError(ALLOWED_PARTNERS, value, 'partner')
        self.__partner = value

    @property
    def organism(self) -> str:
        """ Getter for the organism.

        :return: The organism.
        """
        return self.__organism

    @organism.setter
    def organism(self, value: str) -> None:
        """ Setter for the organism.

        :param value: The organism.
        """
        if not isinstance(value, str):
            raise InputTypeError(str, value, 'organism')
        if value not in self.allowed_organisms:
            raise InputValueError(self.allowed_organisms, value, 'organism')
        self.__organism = value

    @property
    def exposure_conditions(self) -> List[ExposureCondition]:
        """ Getter for the exposure.

        :return: The exposure.
        """
        return self.__exposure_conditions

    @exposure_conditions.setter
    def exposure_conditions(self, value: list) -> None:
        """ Setter for the exposure.

        :param value: The exposure.
        """
        self.__exposure_conditions = []
        if not isinstance(value, list) or not all(isinstance(x, (dict, ExposureCondition)) for x in value):
            raise TypeError("exposure must be a list of ExposureCondition or dict but "
                            "got %s with value %s" % (type(value).__name__, value))
        for exposure_condition in value:
            self.add_exposure_condition(exposure_condition)

    def add_exposure_condition(self, exposure: dict or ExposureCondition) -> None:
        """ Add an exposure condition.

        :param exposure: The exposure condition.
        """
        if isinstance(exposure, ExposureCondition):
            self.__exposure_conditions.append(exposure)
            return None
        elif isinstance(exposure, dict):
            self.__exposure_conditions.append(ExposureCondition(**exposure))
            return None
        raise ValueError('The exposure condition must be a dict or an ExposureCondition object')

    @property
    def exposure_batch(self) -> str:
        """ Getter for the exposure batch.

        :return: The exposure batch.
        """
        return self.__exposure_batch

    @exposure_batch.setter
    def exposure_batch(self, value: str) -> None:
        """ Setter for the exposure batch.

        :param value: The exposure batch.
        """
        if not isinstance(value, str):
            raise InputTypeError(str, value, 'exposure_batch')
        if len(value) > EXPOSURE_BATCH_MAX_LENGTH:
            field_name = 'exposure_batch'
            raise ValueError("%s must be less than %s characters but got %s (value: %s)" % (
                field_name, EXPOSURE_BATCH_MAX_LENGTH, len(value), value
            ))
        if not match(ALLOWED_EXPOSURE_BATCH, value):
            raise InputValueError('AA to ZZ', value, 'exposure_batch')
        self.__exposure_batch = value

    @property
    def replicate4exposure(self) -> int:
        """ Getter for the replicate for exposure.

        :return: The replicate for exposure.
        """
        return self.__replicate4exposure

    @replicate4exposure.setter
    def replicate4exposure(self, value: int) -> None:
        """ Setter for the replicate for exposure.

        :param value: The replicate for exposure.
        """
        if not isinstance(value, int):
            raise InputTypeError(int, value, 'replicate4exposure')
        if value < REPLICATES_EXPOSURE_MIN:
            raise InputMinError(REPLICATES_EXPOSURE_MIN, value, 'replicate4exposure')
        self.__replicate4exposure = value

    @property
    def replicate4control(self) -> int:
        """ Getter for the replicate for exposure.

        :return: The replicate for exposure.
        """
        return self.__replicate4control

    @replicate4control.setter
    def replicate4control(self, value: int) -> None:
        """ Setter for the replicate for exposure.

        :param value: The replicate for exposure.
        """
        if not isinstance(value, int):
            raise InputTypeError(int, value, 'replicate4control')
        if value < REPLICATES_EXPOSURE_MIN:
            raise InputMinError(REPLICATES_CONTROL_MIN, value, 'replicate4control')
        self.__replicate4control = value

    @property
    def replicate_blank(self) -> int:
        """ Getter for the replicate for exposure.

        :return: The replicate for exposure.
        """
        return self.__replicate_blank

    @replicate_blank.setter
    def replicate_blank(self, value: int) -> None:
        """ Setter for the replicate for exposure.

        :param value: The replicate for exposure.
        """
        if not isinstance(value, int):
            raise InputTypeError(int, value, 'replicate_blank')
        if value < REPLICATES_BLANK_RANGE.min or value > REPLICATES_BLANK_RANGE.max:
            raise InputRangeError(REPLICATES_BLANK_RANGE, value, 'replicate_blank')
        self.__replicate_blank = value

    @property
    def start_date(self) -> datetime:
        """ Getter for the start date.

        :return: The start date.
        """
        return self.__start_date

    @start_date.setter
    def start_date(self, value: datetime) -> None:
        """ Setter for the start date.

        :param value: The start date.
        """
        if isinstance(value, datetime):
            self.__start_date = value
            return
        elif isinstance(value, str):
            try:
                self.__start_date = parse_date(value)
                return
            except ValueError:
                raise InputTypeError(datetime, value, 'start_date')
        raise InputTypeError(datetime, value, 'start_date')

    @property
    def end_date(self) -> datetime:
        """ Getter for the end date.

        :return: The end date.
        """
        return self.__end_date

    @end_date.setter
    def end_date(self, value: datetime) -> None:
        """ Setter for the end date.

        :param value: The end date.
        """
        if isinstance(value, datetime):
            self.__end_date = value
            return
        elif isinstance(value, str):
            try:
                self.__end_date = parse_date(value)
                return
            except ValueError:
                raise InputTypeError(datetime, value, 'end_date')
        raise InputTypeError(datetime, value, 'end_date')

    @property
    def timepoints(self) -> int:
        """ Getter for the timepoints.

        :return: The timepoints.
        """
        return self.__timepoints

    @timepoints.setter
    def timepoints(self, value: int) -> None:
        """ Setter for the timepoints.

        :param value: The timepoints.
        """
        if not isinstance(value, int):
            raise InputTypeError(int, value, 'timepoints')
        if value < TIMEPOINTS_RANGE.min or value > TIMEPOINTS_RANGE.max:
            raise InputRangeError(TIMEPOINTS_RANGE, value, 'timepoints')
        self.__timepoints = value

    @property
    def vehicle(self) -> str:
        """ Getter for the vehicle.

        :return: The vehicle.
        """
        return self.__vehicle

    @vehicle.setter
    def vehicle(self, value: str) -> None:
        """ Setter for the vehicle.

        :param value: The vehicle.
        """
        if not isinstance(value, str):
            raise InputTypeError(str, value, 'vehicle')
        if value not in ALLOWED_VEHICLES:
            raise InputValueError(ALLOWED_VEHICLES, value, 'vehicle')
        self.__vehicle = value

    @property
    def timepoint_zero(self) -> bool:
        """ Getter for the timepoint zero.

        :return: The timepoint zero.
        """
        return self.__timepoint_zero

    @timepoint_zero.setter
    def timepoint_zero(self, value: bool) -> None:
        """ Setter for the timepoint zero. """
        if not isinstance(value, bool):
            raise InputTypeError(bool, value, 'timepoint_zero')
        self.__timepoint_zero = value

    def __iter__(self):
        """ Iterator for the class. Used to serialize the object to a dictionary.

        :return: The iterator.
        """
        iters = {
            "partner": self.partner,
            "organism": self.organism,
            "exposure_conditions": [dict(exposure_condition) for exposure_condition in self.exposure_conditions],
            "exposure_batch": self.exposure_batch,
            "replicate4exposure": self.replicate4exposure,
            "replicate4control": self.replicate4control,
            "replicate_blank": self.replicate_blank,
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "timepoints": self.timepoints,
            "vehicle": self.vehicle
        }
        for key, value in iters.items():
            yield key, value

    def __get_array_of_unique_chemicals(self) -> List[str]:
        """ Get an array of unique chemicals from the exposure conditions.

        :return: The array of unique chemicals names.
        """
        array_of_unique_chemicals: list[str] = []
        for exposure_condition in self.exposure_conditions:
            for chemical in exposure_condition.chemicals_name:
                if chemical not in array_of_unique_chemicals:
                    array_of_unique_chemicals.append(chemical)
        return array_of_unique_chemicals

    def to_dataframe(self) -> tuple[DataFrame, DataFrame]:
        """ Convert the object to a pandas DataFrame.

        :return: The pandas DataFrame.
        """
        sample_dataframe: DataFrame = build_sample_dataframe(
            harvester=self, organism_code=get_organism_code(self.organism),
            chemicals_mapping=get_chemical_code_mapping(self.__get_array_of_unique_chemicals())
        )
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
