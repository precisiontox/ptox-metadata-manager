""" A module to parse chemicals from XLSX file.
"""
from __future__ import annotations

from pandas import read_excel, DataFrame

from ptmd.const import CHEMICALS_FILEPATH


def parse_chemicals() -> list[dict]:
    """ Parse chemicals from XLSX file.

    :return: A list of chemicals.
    """
    chemicals: list[dict] = []
    chemicals_dataframe: DataFrame = read_excel(CHEMICALS_FILEPATH,
                                                engine='openpyxl',
                                                sheet_name="SUMMARY table of CHEMICALS")
    for compound in chemicals_dataframe.itertuples():
        chemicals.append({
            'common_name': compound.Compound.replace('"', ''),
            'ptx_code': int(compound._2.replace('"', '').replace('PTX', '')),
            'formula': compound.Formula.replace('"', ''),
            'cas': compound._5.replace('"', '').split('\n')[0]
        })
    return chemicals
