""" A module to extract data from spreadsheets.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from pandas import ExcelFile, DataFrame

from ptmd.logger import LOGGER
from ptmd.database.queries import get_chemicals_from_name


def extract_data_from_spreadsheet(filepath: str) -> dict | None:
    """ Given a xlsx file, extract the data from the spreadsheet and return it as a dictionary.

    :param filepath: the path to the xlsx file
    :return: a dictionary containing the data from the spreadsheet
    """
    try:
        file_handler: ExcelFile = ExcelFile(filepath, engine='openpyxl')
        general_information: dict = file_handler.parse("General Information").to_dict(orient='records')[0]
        exposure_information: DataFrame = file_handler.parse("Exposure information")
        return {
            'replicates': general_information['replicates'],
            'controls': general_information['control'],
            'blanks': general_information['blanks'],
            'vehicle_name': general_information['compound_vehicle'],
            'chemicals': get_chemicals_from_name(list(exposure_information['compound_name'].unique()))
        }
    except Exception as e:
        LOGGER.error(f'Error while extracting data from spreadsheet: {e}')
        return None
