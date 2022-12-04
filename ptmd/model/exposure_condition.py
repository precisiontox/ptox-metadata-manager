from ptmd.model.const import ALLOWED_CHEMICAL_NAMES, ALLOWED_DOSE_VALUES
from ptmd.model.exceptions import InputTypeError, InputValueError
from ptmd.model.utils import get_field_name


class ExposureCondition:
    __chemical_name: str or None = None
    __dose: str or None = None

    def __init__(self, chemical_name: str, dose: str) -> None:
        self.chemical_name = chemical_name
        self.dose = dose

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
            raise InputTypeError(str, value, get_field_name(self, 'dose'))
        if value not in ALLOWED_DOSE_VALUES:
            raise InputValueError(ALLOWED_DOSE_VALUES, value, get_field_name(self, 'dose'))
        self.__dose = value

    def __eq__(self, other):
        return self.__dose == other.__dose and self.__chemical_name == other.__chemical_name

    def __ne__(self, other):
        return not self.__eq__(other)
