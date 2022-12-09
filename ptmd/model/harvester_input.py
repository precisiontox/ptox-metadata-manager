""" This module contains the class for the input of the harvester.

@author: Terazus (D. Batista)
"""

from re import match
from typing import List
from datetime import datetime

from dateutil.parser import parse as parse_date
from pandas import DataFrame, Series, concat as pandas_concat, ExcelWriter

from ptmd.const import (
    ALLOWED_PARTNERS, ALLOWED_ORGANISMS, ALLOWED_EXPOSURE_BATCH, EXPOSURE_BATCH_MAX_LENGTH,
    REPLICATES_EXPOSURE_MIN, REPLICATES_CONTROL_MIN,
    REPLICATES_BLANK_RANGE,
    SAMPLE_SHEET_BASE_COLUMNS, GENERAL_SHEET_BASE_COLUMNS
)
from ptmd.model.exceptions import InputTypeError, InputValueError, InputMinError, InputRangeError
from ptmd.model.exposure_condition import ExposureCondition
from ptmd.model.utils import get_field_name


class HarvesterInput:
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
                 exposure_conditions: List[dict] or List[ExposureCondition] = None) -> None:
        """ The harvester constructor """
        self.partner = partner
        self.organism = organism
        self.exposure_conditions = exposure_conditions if exposure_conditions else []
        self.exposure_batch = exposure_batch
        self.replicate4exposure = replicate4exposure
        self.replicate4control = replicate4control
        self.replicate_blank = replicate_blank
        self.start_date = start_date
        self.end_date = end_date
        self.file_path = None

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
            raise InputTypeError(str, value, get_field_name(self, 'partner'))
        if value not in ALLOWED_PARTNERS:
            raise InputValueError(ALLOWED_PARTNERS, value, get_field_name(self, 'partner'))
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
            raise InputTypeError(str, value, get_field_name(self, 'organism'))
        if value not in ALLOWED_ORGANISMS:
            raise InputValueError(ALLOWED_ORGANISMS, value, get_field_name(self, 'organism'))
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
            raise TypeError("HarvesterInput.exposure must be a list of ExposureCondition or dict but "
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
            raise InputTypeError(str, value, get_field_name(self, 'exposure_batch'))
        if len(value) > EXPOSURE_BATCH_MAX_LENGTH:
            field_name = get_field_name(self, 'exposure_batch')
            raise ValueError("%s must be less than %s characters but got %s (value: %s)" % (
                field_name, EXPOSURE_BATCH_MAX_LENGTH, len(value), value
            ))
        if not match(ALLOWED_EXPOSURE_BATCH, value):
            raise InputValueError('AA to ZZ', value, get_field_name(self, 'exposure_batch'))
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
            raise InputTypeError(int, value, get_field_name(self, 'replicate4exposure'))
        if value < REPLICATES_EXPOSURE_MIN:
            raise InputMinError(REPLICATES_EXPOSURE_MIN, value, get_field_name(self, 'replicate4exposure'))
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
            raise InputTypeError(int, value, get_field_name(self, 'replicate4control'))
        if value < REPLICATES_EXPOSURE_MIN:
            raise InputMinError(REPLICATES_CONTROL_MIN, value, get_field_name(self, 'replicate4control'))
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
            raise InputTypeError(int, value, get_field_name(self, 'replicate_blank'))
        if value < REPLICATES_BLANK_RANGE.min or value > REPLICATES_BLANK_RANGE.max:
            raise InputRangeError(REPLICATES_BLANK_RANGE,
                                  value, get_field_name(self, 'replicate_blank'))
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
                raise InputTypeError(datetime, value, get_field_name(self, 'start_date'))
        raise InputTypeError(datetime, value, get_field_name(self, 'start_date'))

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
                raise InputTypeError(datetime, value, get_field_name(self, 'end_date'))
        raise InputTypeError(datetime, value, get_field_name(self, 'end_date'))

    def __iter__(self):
        """ Iterator for the class. Used to serialize the object to a dictionary.

        :return: The iterator.
        """
        iters = {
            'partner': self.partner,
            'organism': self.organism,
            'exposure_conditions': [dict(exposure_condition) for exposure_condition in self.exposure_conditions],
            'exposure_batch': self.exposure_batch,
            'replicate4exposure': self.replicate4exposure,
            'replicate4control': self.replicate4control,
            'replicate_blank': self.replicate_blank,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d')
        }
        for key, value in iters.items():
            yield key, value

    def to_dataframe(self) -> tuple[DataFrame, DataFrame]:
        """ Convert the object to a pandas DataFrame.

        :return: The pandas DataFrame.
        """
        sample_dataframe = DataFrame(columns=SAMPLE_SHEET_BASE_COLUMNS)
        general_dataframe = DataFrame(columns=GENERAL_SHEET_BASE_COLUMNS)
        general_series = Series([
            self.partner,
            self.organism,
            self.exposure_batch,
            self.replicate4control,
            self.replicate_blank,
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d'),
        ], index=general_dataframe.columns)
        general_dataframe = pandas_concat([general_dataframe, general_series.to_frame().T],
                                          ignore_index=False, sort=False, copy=False)
        for chemical in self.exposure_conditions:
            for replicate in range(self.replicate4exposure):
                for dose in chemical.doses:
                    series = Series([
                        '', '', '', '', '', '', '', '',
                        replicate + 1,
                        chemical.chemical_name,
                        dose
                    ], index=sample_dataframe.columns)
                    sample_dataframe = pandas_concat([sample_dataframe, series.to_frame().T],
                                                     ignore_index=False, sort=False, copy=False)
        return sample_dataframe, general_dataframe

    def save(self, path: str) -> str:
        """ Save the sample sheet to a file.

        :param path: The path to the file.
        :return: The path to the file the sample sheet was saved to.
        """
        dataframes = self.to_dataframe()
        writer = ExcelWriter(path)
        dataframes[1].to_excel(writer,
                               sheet_name='General Information', index=False, columns=GENERAL_SHEET_BASE_COLUMNS)
        dataframes[0].to_excel(writer,
                               sheet_name='SAMPLE_TEST', columns=SAMPLE_SHEET_BASE_COLUMNS, index=False)
        writer.close()
        self.file_path = path
        return path
