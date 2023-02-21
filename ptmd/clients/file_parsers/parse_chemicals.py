""" A module to parse chemicals from XLSX file.

@Author: D. Batista (Terazus)
"""
from math import isnan

from pandas import read_excel, DataFrame

from ptmd.const import CHEMICALS_FILEPATH
from ptmd.logger import LOGGER


class Compound:
    """ A class to represent a chemical compound.

    :param ptx_code: the ptx code of the compound.
    :param name: the common name of the compound.
    :param formula: the chemical formula of the compound.
    :param cas: the CAS number of the compound.
    """

    def __init__(self, ptx_code: float or str, name: str, formula: str, cas: str) -> None:
        """ Constructor method. """
        self.common_name: str = name
        self.ptx_code: int = ptx_code
        self.cas: str = cas
        self.formula: str = formula

    @property
    def common_name(self) -> str:
        """ Getter for thhe common name of the compound.

        :return: the common name of the compound.
        """
        return self.__common_name

    @common_name.setter
    def common_name(self, value: str) -> None:
        """ Setter for the common name of the compound.

        :param value: the common name of the compound.
        """
        self.__common_name = self.clean_string(value)

    @property
    def ptx_code(self) -> int:
        """ Getter for the ptx code of the compound.

        :return: the ptx code of the compound.
        """
        return self.__ptx_code

    @ptx_code.setter
    def ptx_code(self, value: str or float) -> None:
        """ Setter for the ptx code of the compound.

        @param value: the ptx code of the compound.
        """
        if type(value).__name__ == 'float' and isnan(value):
            raise ValueError('ptx_code cannot be nan for compound %s' % self.__common_name)
        if value == '-':
            raise ValueError('ptx_code needs to be a valid string but got "-" for compound %s' % self.__common_name)
        value = int(self.clean_string(value).replace('PTX', ''))
        self.__ptx_code = value

    @property
    def cas(self) -> str:
        """ Getter for the CAS number of the compound.

        :return: the CAS number of the compound.
        """
        return self.__cas

    @cas.setter
    def cas(self, value: str or float) -> None:
        """ Setter for the CAS number of the compound.

        @param value: the CAS number of the compound.
        """
        if type(value).__name__ == 'float' and isnan(value):
            raise ValueError('CAS cannot be nan for compound %s' % self.__common_name)
        self.__cas = self.clean_string(value)

    @property
    def formula(self) -> str:
        """ Getter for the chemical formula of the compound.

        :return: the chemical formula of the compound.
        """
        return self.__formula

    @formula.setter
    def formula(self, value: str or float):
        """ Setter for the chemical formula of the compound.

        @param value: the chemical formula of the compound.
        """
        if type(value).__name__ == 'float' and isnan(value):
            raise ValueError('formula cannot be nan for compound %s' % self.__common_name)
        self.__formula = self.clean_string(value)

    @staticmethod
    def clean_string(value: str) -> str:
        """ Cleans a string from unwanted characters and strip whitespaces before and after the string.

        :param value: the string to be cleaned.
        :return: the cleaned string.
        """
        val: str = value.replace('\n', '')
        if 'New:' in val:
            val = val.split('New:')[-1]
        if '(' in val:
            val = val.split('(')[0]
        if '·' in value:
            val = val.split('·')[0]
        return val.strip()

    def __iter__(self) -> None:
        """ Iterator method used to convert the object into a dictionary. """
        data = {
            'common_name': self.__common_name,
            'ptx_code': self.__ptx_code,
            'formula': self.__formula,
            'name_hash_id': self.__cas
        }
        for k, v in data.items():
            yield k, v


def parse_chemicals() -> list[dict]:
    """ Pulls the chemicals from the XLSX files and validate them with the Compound class.

    :return: a list of chemicals from the ptox database.
    """
    chemicals: list[Compound] = []
    chemicals_dataframe: DataFrame = read_excel(CHEMICALS_FILEPATH, engine='openpyxl')

    for compound in chemicals_dataframe.itertuples():
        name: str = compound.Compound
        formula: str = compound.Formula
        cas: str = compound._5
        ptx_code: str or float = compound._2
        try:
            chemicals.append(Compound(ptx_code=ptx_code, name=name, formula=formula, cas=cas))
        except Exception as error:
            LOGGER.warning(error)
    return [dict(compound) for compound in chemicals]
