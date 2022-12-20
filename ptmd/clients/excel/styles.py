""" Excel submodule that contains the styling functions. Consumes the format functions outputs.

@author: D. Batista (Terazus)
"""

from typing import Any

from pandas import ExcelWriter
from xlsxwriter.workbook import Format
from .formats import get_header_format, get_extra_cells_format, get_empty_cells_format


def style_sheets(writer: ExcelWriter) -> None:
    """ Style the sheets.

    :param writer: The writer to use.
    """
    style_sample_sheet(writer)
    style_general_sheet(writer)


def style_sample_sheet(writer: ExcelWriter) -> None:
    """ Style the sample sheet.

    :param writer: The writer to use.
    """
    header_format: Format = get_header_format(writer)
    extra_cells_format: Format = get_extra_cells_format(writer)
    empty_cells_format: Format = get_empty_cells_format(writer)
    worksheet: Any = writer.sheets['Exposure conditions']
    worksheet.protect()

    worksheet.set_row(0, 50, cell_format=header_format)
    worksheet.set_column('A:A', 25, cell_format=empty_cells_format)
    worksheet.set_column('B:B', 30, cell_format=empty_cells_format)
    worksheet.set_column('C:D', 15, cell_format=empty_cells_format)
    worksheet.set_column('D:D', 20, cell_format=empty_cells_format)
    worksheet.set_column('E:H', 30, cell_format=empty_cells_format)
    worksheet.set_column('I:I', 15, cell_format=extra_cells_format)
    worksheet.set_column('J:J', 30, cell_format=extra_cells_format)
    worksheet.set_column('K:L', 15, cell_format=extra_cells_format)
    worksheet.set_column('M:M', 30, cell_format=extra_cells_format)


def style_general_sheet(writer: ExcelWriter) -> None:
    """ Style the general sheet.

    :param writer: The writer to use.
    """
    formatter: Format = get_header_format(writer)
    extra_cells_format: Format = get_extra_cells_format(writer)
    worksheet: Any = writer.sheets['General Information']
    worksheet.set_row(0, 50, cell_format=formatter)
    worksheet.set_column('A:J', 25, cell_format=extra_cells_format)
