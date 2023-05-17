""" A module to extract data from spreadsheets.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from pandas import ExcelFile

from ptmd.logger import LOGGER


def extract_data_from_spreadsheet(filepath: str) -> dict | None:
    """ Given a xlsx file, extract the data from the spreadsheet and return it as a dictionary.

    :param filepath: the path to the xlsx file
    :return: a dictionary containing the data from the spreadsheet
    """
    try:
        file_handler: ExcelFile = ExcelFile(filepath, engine='openpyxl')
        general_information: dict = file_handler.parse("General Information").to_dict(orient='records')[0]
        return {
            'replicates': general_information['replicates'],
            'controls': general_information['control'],
            'blanks': general_information['blanks'],
            'vehicle_name': general_information['compound_vehicle'],
        }
    except Exception as e:
        LOGGER.error(f'Error while extracting data from spreadsheet: {e}')
        return None
