""" A module to parse chemicals from XLSX file.
"""
from __future__ import annotations

from pandas import read_csv, DataFrame

from ptmd.const import CHEMICALS_FILEPATH, BASE_IDENTIFIER


def parse_chemicals() -> list[dict]:
    """ Parse chemicals from XLSX file.

    :return: A list of chemicals.
    """
    chemicals: list[dict] = []
    chemicals_dataframe: DataFrame = read_csv(CHEMICALS_FILEPATH, sep=",", encoding='utf-8')
    for compound in chemicals_dataframe.itertuples():
        chemicals.append({
            'common_name': compound.compound_name_user,
            'ptx_code': int(compound.ptx_code.replace(BASE_IDENTIFIER, '')),
            'formula': compound.formula,
            'cas': compound.cas_neutral
        })
    return chemicals
