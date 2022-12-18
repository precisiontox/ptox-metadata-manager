""" Module to created spreadsheets from the HarvesterInput, style and save them to disk.

@author: D. Batista (Terazus)
"""
from typing import Any

from pandas import DataFrame, Series, ExcelWriter, concat as pd_concat
from pandas.io.formats.excel import ExcelFormatter
from pandas.io.formats.style import Styler
from xlsxwriter.workbook import Format

from ptmd.const import GENERAL_SHEET_COLUMNS, SAMPLE_SHEET_COLUMNS, DOSE_MAPPING, TIME_POINT_MAPPING
from .interfaces import HarvesterInput


def build_general_dataframe(
        harvester: HarvesterInput
) -> DataFrame:
    """ Builds a DataFrame with the general information of the harvester.

    :param harvester: The harvester to build the DataFrame from.
    :return: A DataFrame with the general information of the harvester.
    """
    dataframe = DataFrame(columns=GENERAL_SHEET_COLUMNS)
    series = Series([
        harvester.partner,
        harvester.organism,
        harvester.exposure_batch,
        harvester.replicate4control,
        harvester.replicate4exposure,
        harvester.replicate_blank,
        harvester.start_date.strftime('%Y-%m-%d'),
        harvester.end_date.strftime('%Y-%m-%d'),
        harvester.timepoints,
        harvester.vehicle,
    ], index=dataframe.columns)
    return series.to_frame().T


def build_sample_dataframe(
        harvester: HarvesterInput,
        chemicals_mapping: dict[str, str],
        organism_code: str
) -> DataFrame:
    """ Builds a DataFrame with the sample information of the harvester.

    :param harvester: The harvester to build the DataFrame from.
    :param chemicals_mapping: A dictionary mapping chemicals names to ptox codes.
    :param organism_code: The organism code to use.
    :return: A DataFrame
    """
    dataframe: DataFrame = DataFrame(columns=SAMPLE_SHEET_COLUMNS)
    for exposure_condition in harvester.exposure_conditions:
        dose_code: str = DOSE_MAPPING[exposure_condition.dose]
        for chemical in exposure_condition.chemicals_name:
            chemical_code: str = chemicals_mapping[chemical]
            for tp in range(1, harvester.timepoints + 1):
                timepoint: str = f'TP{tp}'
                timepoint_code: str = TIME_POINT_MAPPING[timepoint]
                for replicate in range(1, harvester.replicate4exposure + 1):
                    hash_id: str = '%s%s%s%s%s%s' % (organism_code, harvester.exposure_batch, chemical_code,
                                                     dose_code, timepoint_code, replicate)
                    series: Series = Series([
                        '', '', '', '', '', '', '', '',
                        replicate, chemical, exposure_condition.dose, 'TP%s' % tp, hash_id
                    ], index=dataframe.columns)
                    dataframe = pd_concat([dataframe, series.to_frame().T], ignore_index=False, sort=False, copy=False)
                for replicate in range(1, harvester.replicate4control + 1):
                    hash_id: str = '%s%s%s%sZ%s' % (organism_code, harvester.exposure_batch, chemical_code,
                                                    timepoint_code, replicate)
                    series: Series = Series([
                        '', '', '', '', '', '', '', '',
                        replicate, "CONTROL (%s)" % harvester.vehicle, 0, 'TP%s' % tp, hash_id
                    ], index=dataframe.columns)
                    dataframe = pd_concat([dataframe, series.to_frame().T], ignore_index=False, sort=False, copy=False)
    return add_blanks_to_sample_dataframe(dataframe, harvester.replicate_blank, organism_code, harvester.exposure_batch)


def add_blanks_to_sample_dataframe(
        sample_df: DataFrame,
        replicate_blank: int,
        organism_code: str,
        exposure_batch: str
) -> DataFrame:
    """ Add the blanks to the sample dataframe.

    :param sample_df: The sample dataframe.
    :param replicate_blank: The number of blanks to add.
    :param organism_code: The organism code to use.
    :param exposure_batch: The exposure batch to use.
    :return: The sample dataframe with the blanks.
    """
    for blank in range(1, replicate_blank + 1):
        hash_id = '%s%s998ZS%s' % (organism_code, exposure_batch, blank)
        series = Series(['', '', '', '', '', '', '', '', blank, 'EXTRACTION BLANK', "0", 'TP0', hash_id],
                        index=sample_df.columns)
        sample_df = pd_concat([sample_df, series.to_frame().T], ignore_index=False, sort=False, copy=False)
    return sample_df


def save_to_excel(dataframes: tuple[DataFrame, DataFrame], path: str):
    """ Save the dataframes to an Excel file.

    :param dataframes: The dataframes to save.
    :param path: The path to save the file to.
    """
    ExcelFormatter.header_style = None  # Trick to remove the default header style.
    general_df: DataFrame = dataframes[1]
    sample_df: DataFrame = dataframes[0]

    with ExcelWriter(path, engine="xlsxwriter") as writer:
        general_df.to_excel(writer, sheet_name='General Information', columns=GENERAL_SHEET_COLUMNS, index=False)
        sample_df.to_excel(writer, sheet_name='Exposure conditions', columns=SAMPLE_SHEET_COLUMNS, index=False)

        sample_styler: Styler = sample_df.reset_index(drop=True).style
        sample_styler.applymap_index(style_headers, axis="columns")
        sample_styler.applymap(style_cells, subset=SAMPLE_SHEET_COLUMNS[8:13])
        sample_styler.applymap(style_cells, empty=True, subset=SAMPLE_SHEET_COLUMNS[0:8])
        sample_styler.to_excel(writer, sheet_name='Exposure conditions', columns=SAMPLE_SHEET_COLUMNS, index=False)

        writer.sheets['General Information'].set_column('A:J', 25)
        general_styler: Styler = general_df.reset_index(drop=True).style
        general_styler.applymap_index(style_headers, axis="columns")
        general_styler.applymap(style_cells, empty=True, subset=GENERAL_SHEET_COLUMNS[0:10])
        general_styler.to_excel(writer, sheet_name='General Information', columns=GENERAL_SHEET_COLUMNS, index=False)

        formatter: Format = writer.book.add_format({'bold': True, 'valign': 'vcenter'})
        worksheet: Any = writer.sheets['Exposure conditions']
        worksheet.set_row(0, 50, cell_format=formatter)
        style_sample_sheet_cells_width(worksheet)

    return path


def style_cells(s: Any, empty=False) -> str:
    """ Style the cells of the sample sheet.

    :param s: the subset item to style.
    :param empty: whether the cell is empty or not.
    :return: the style to apply.
    """
    common_properties: str = 'border: 1px solid black;'
    if not empty:
        return 'font-size: 18px; text-align: center; background-color: #efefef;' + common_properties
    return 'font-size: 16px;' + common_properties


def style_headers(s: Any) -> str:
    """ Styles the headers of the spreadsheet.

    :param s: the subset item to style.
    :return: the style to apply.
    """
    return """font-size: 20px; text-align: center; background-color: #008080; border: 3px solid black;"""


def style_sample_sheet_cells_width(worksheet: Any) -> Any:
    """ Styles the sample worksheet cells width.

    :param worksheet: The pandas ExcelWriter worksheet.
    :return: The sample worksheet with the column width properly set.
    """
    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 30)
    worksheet.set_column('C:D', 15)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 30)
    worksheet.set_column('F:G', 35)
    worksheet.set_column('H:H', 30)
    worksheet.set_column('I:I', 13)
    worksheet.set_column('J:J', 30)
    worksheet.set_column('K:L', 15)
    worksheet.set_column('M:M', 35)
    worksheet.set_column('N:Z', 1)
    return worksheet
