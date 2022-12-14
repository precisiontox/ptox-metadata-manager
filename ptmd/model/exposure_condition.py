""" This module contains the ExposureCondition class.

@author: Terazus (D. Batista)
"""
from ptmd.const import ALLOWED_DOSE_VALUES
from ptmd.model.exceptions import InputTypeError, InputValueError
from ptmd.database import get_allowed_chemicals
from .interfaces import ExposureCondition as ExposureConditionInterface


class ExposureCondition(ExposureConditionInterface):
    """ The ExposureCondition is an object with a chemical name and a dose value.

    :param chemicals_name: The name of the chemical.
    :param dose: a list of dose for that chemical.
    """

    def __init__(self, chemicals_name: list[str], dose: str) -> None:
        """ Exposition with a chemical as a given dose. """
        self.allowed_chemicals = get_allowed_chemicals()
        self.chemicals_name = chemicals_name
        self.dose = dose

    @property
    def chemicals_name(self) -> list[str]:
        """ Getter for the chemical name.

        :return: The chemical name.
        """
        return self.__chemicals_name

    @chemicals_name.setter
    def chemicals_name(self, values: list[str]) -> None:
        """ Setter for the chemicals name.

        :param values: The list of chemicals name.
        """
        if not isinstance(values, list):
            raise InputTypeError(list, values, 'chemicals_name')
        for chemical_name in values:
            if not isinstance(chemical_name, str):
                raise InputTypeError(str, chemical_name, 'chemicals_name')
            if chemical_name not in self.allowed_chemicals:
                raise InputValueError("/api/chemicals", chemical_name, 'chemicals_name')
        self.__chemicals_name = values

    @property
    def dose(self) -> str:
        """ Getter for the dose.

        :return: The dose.
        """
        return self.__dose

    @dose.setter
    def dose(self, value: str) -> None:
        """ Setter for the dose.

        :param value: The dose.
        """
        if not isinstance(value, str):
            raise InputTypeError(str, value, 'dose')
        if value not in ALLOWED_DOSE_VALUES:
            raise InputValueError(ALLOWED_DOSE_VALUES, value, 'dose')
        self.__dose = value

    def __eq__(self, other) -> bool:
        """ Equality operator.

        :param other: The other object to compare to.
        :return: True if the objects are equal, False otherwise.
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """ Inequality operator.

        :param other: The other object to compare to.
        :return: True if the objects are not equal, False otherwise.
        """
        return not self.__eq__(other)

    def __iter__(self) -> iter:
        """ Iterator for the object. Used to serialize the object as a dictionary.

        :return: The iterator.
        """
        iters = {
            'chemicals_name': self.__chemicals_name,
            'dose': self.__dose
        }
        for key, value in iters.items():
            yield key, value
