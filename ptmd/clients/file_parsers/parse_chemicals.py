from math import isnan

from pandas import read_excel, DataFrame

from ptmd.const import CHEMICALS_FILEPATH
from ptmd.logger import LOGGER


class Compound:

    def __init__(self, ptx_code: float or str, name: str, formula: str, cas: str) -> None:
        self.common_name: str = name
        self.ptx_code: int = ptx_code
        self.cas: str = cas
        self.formula: str = formula

    @property
    def common_name(self) -> str:
        return self.__common_name

    @common_name.setter
    def common_name(self, value: str) -> None:
        self.__common_name = self.clean_string(value)

    @property
    def ptx_code(self) -> int:
        return self.__ptx_code

    @ptx_code.setter
    def ptx_code(self, value: str or float) -> None:
        if type(value).__name__ == 'float' and isnan(value):
            raise ValueError('ptx_code cannot be nan for compound %s' % self.__common_name)
        if value == '-':
            raise ValueError('ptx_code needs to be a valid string but got "-" for compound %s' % self.__common_name)
        value = int(self.clean_string(value).replace('PTX', ''))
        self.__ptx_code = value

    @property
    def cas(self):
        return self.__cas

    @cas.setter
    def cas(self, value):
        if type(value).__name__ == 'float' and isnan(value):
            raise ValueError('CAS cannot be nan for compound %s' % self.__common_name)
        self.__cas = self.clean_string(value)

    @property
    def formula(self):
        return self.__formula

    @formula.setter
    def formula(self, value):
        if type(value).__name__ == 'float' and isnan(value):
            raise ValueError('formula cannot be nan for compound %s' % self.__common_name)
        self.__formula = self.clean_string(value)

    @staticmethod
    def clean_string(value: str) -> str:
        val: str = value.replace('\n', '')
        if 'New:' in val:
            val = val.split('New:')[-1]
        if '(' in val:
            val = val.split('(')[0]
        if '·' in value:
            val = val.split('·')[0]
        return val.strip()

    def __iter__(self):
        data = {
            'common_name': self.__common_name,
            'ptx_code': self.__ptx_code,
            'formula': self.__formula,
            'name_hash_id': self.__cas
        }
        for k, v in data.items():
            yield k, v


def parse_chemicals() -> list[dict]:
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
