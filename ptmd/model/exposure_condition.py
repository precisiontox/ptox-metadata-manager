""" This module contains the ExposureCondition class.

@author: Terazus (D. Batista)
"""
from ptmd.const import ALLOWED_CHEMICAL_NAMES, ALLOWED_DOSE_VALUES
from ptmd.model.exceptions import InputTypeError, InputValueError
from ptmd.model.utils import get_field_name


class ExposureCondition:
    """ The ExposureCondition is an object with a chemical name and a dose value.

    :param chemical_name:
    :param doses:
    """

    def __init__(self, chemical_name: str, doses: list[str]) -> None:
        """ Exposition with a chemical as a given dose. """
        self.chemical_name = chemical_name
        self.doses = doses

    @property
    def chemical_name(self) -> str:
        """ Getter for the chemical name.

        :return: The chemical name.
        """
        return self.__chemical_name

    @chemical_name.setter
    def chemical_name(self, value: str) -> None:
        """ Setter for the chemical name.

        :param value: The chemical name.
        """
        if not isinstance(value, str):
            raise InputTypeError(str, value, get_field_name(self, 'chemical_name'))
        if value not in ALLOWED_CHEMICAL_NAMES:
            raise InputValueError(ALLOWED_CHEMICAL_NAMES, value, get_field_name(self, 'chemical_name'))
        self.__chemical_name = value

    @property
    def doses(self) -> list[str]:
        """ Getter for the dose.

        :return: The dose.
        """
        return self.__doses

    @doses.setter
    def doses(self, values: list[str]) -> None:
        """ Setter for the dose.

        :param values: The dose.
        """
        if not isinstance(values, list):
            raise InputTypeError(list, values, get_field_name(self, 'dose'))
        for value in values:
            if value not in ALLOWED_DOSE_VALUES:
                raise InputValueError(ALLOWED_DOSE_VALUES, value, get_field_name(self, 'dose'))
        self.__doses = values

    def __eq__(self, other) -> bool:
        """ Equality operator.

        :param other: The other object to compare to.
        :return: True if the objects are equal, False otherwise.
        """
        return self.__doses == other.__doses and self.__chemical_name == other.__chemical_name

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
            'chemical_name': self.__chemical_name,
            'doses': self.__doses
        }
        for key, value in iters.items():
            yield key, value
