from re import match

from typing import List

from ptmd.model.const import (
    ALLOWED_PARTNERS, ALLOWED_ORGANISMS, ALLOWED_EXPOSURE_BATCH,
    REPLICATES_EXPOSURE_MIN, REPLICATES_CONTROL_MIN,
    REPLICATES_BLANK_RANGE
)
from ptmd.model.exceptions import InputTypeError, InputValueError, InputMinError, InputRangeError
from ptmd.model.exposure_condition import ExposureCondition
from ptmd.model.utils import get_field_name


class HarvesterInput:
    def __init__(self,
                 partner: str,
                 organism: str,
                 exposure_batch: str,
                 replicate4exposure: int,
                 replicate4control: int,
                 replicate_blank: int,
                 exposure_conditions: List[dict] = None) -> None:
        self.partner = partner
        self.organism = organism
        self.exposure_conditions = exposure_conditions if exposure_conditions else []
        self.exposure_batch = exposure_batch
        self.replicate4exposure = replicate4exposure
        self.replicate4control = replicate4control
        self.replicate_blank = replicate_blank

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
        if not isinstance(value, list):
            raise InputTypeError(list, value, get_field_name(self, 'exposure'))
        self.__exposure_conditions = [ExposureCondition(**exposure) for exposure in value]

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
