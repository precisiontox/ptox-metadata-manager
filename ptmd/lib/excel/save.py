""" Excel submodule that contains the save function

 @author: D. Batista (Terazus)
"""

from pandas import DataFrame, ExcelWriter
from pandas.io.formats.excel import ExcelFormatter

from ptmd.const import GENERAL_SHEET_COLUMNS, SAMPLE_SHEET_COLUMNS
from .styles import style_sheets


def save_to_excel(dataframes: tuple[DataFrame, DataFrame], path: str):
    """ Save the dataframes to an Excel file.

    :param dataframes: The dataframes to save.
    :param path: The path to save the file to.
    """
    ExcelFormatter.header_style = None
    general_df: DataFrame = dataframes[1]
    sample_df: DataFrame = dataframes[0]

    with ExcelWriter(path, engine="xlsxwriter") as writer:
        sample_df.to_excel(writer, sheet_name='Exposure information', columns=SAMPLE_SHEET_COLUMNS, index=False)
        general_df.to_excel(writer, sheet_name='General Information', columns=GENERAL_SHEET_COLUMNS, index=False)
        style_sheets(writer)
    return path
