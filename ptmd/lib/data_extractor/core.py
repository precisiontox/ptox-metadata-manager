""" A module to extract data from spreadsheets.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from json import loads as json_loads

from pandas import ExcelFile, DataFrame

from ptmd.database.queries import get_chemicals_from_name, create_timepoints_hours


def extract_data_from_spreadsheet(filepath: str) -> dict | None:
    """ Given a xlsx file, extract the data from the spreadsheet and return it as a dictionary.

    :param filepath: the path to the xlsx file
    :return: a dictionary containing the data from the spreadsheet
    """
    file_handler: ExcelFile = ExcelFile(filepath, engine='openpyxl')
    general_information: dict = file_handler.parse("General Information").to_dict(orient='records')[0]
    exposure_information: DataFrame = file_handler.parse("Exposure information")
    timepoints_values: list[int] = json_loads(general_information['timepoints'])
    return {
        'replicates': general_information['replicates'],
        'controls': general_information['control'],
        'blanks': general_information['blanks'],
        'vehicle_name': general_information['compound_vehicle'],
        'timepoints': create_timepoints_hours(timepoints_values),
        'chemicals': get_chemicals_from_name(list(exposure_information['compound_name'].unique()))
    }
