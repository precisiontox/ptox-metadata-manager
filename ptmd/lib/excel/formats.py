""" Excel submodule containing ExcelWriter formats.

@author: D. Batista (Terazus)
"""
from pandas import ExcelWriter
from xlsxwriter.workbook import Format


def set_common_formats(formatter: Format) -> Format:
    """ Set the common formats.

    :return: The common formats.
    """
    formatter.set_font_name('Arial')
    formatter.set_text_wrap()
    formatter.set_align('center')
    return formatter


def get_header_format(writer: ExcelWriter) -> Format:
    """ Get the sample formatter.

    :param writer: The writer to use.
    :return: The sample formatter.
    """
    formatter: Format = writer.book.add_format()
    formatter = set_common_formats(formatter)
    formatter.set_bg_color('#008080')
    formatter.set_color('white')
    formatter.set_font_size(12)
    # formatter.set_bold()
    formatter.set_border(5)
    formatter.set_align('vcenter')
    return formatter


def get_empty_cells_format(writer: ExcelWriter) -> Format:
    """ Get the cell formatter.

    :param writer: The writer to use.
    :return: The cell formatter.
    """
    formatter: Format = writer.book.add_format()
    formatter = set_common_formats(formatter)
    formatter.set_font_size(12)
    formatter.set_border(1)
    formatter.set_locked(False)
    return formatter


def get_extra_cells_format(writer: ExcelWriter) -> Format:
    """ Get the cell formatter.

    :param writer: The writer to use.
    :return: The cell formatter.
    """
    formatter: Format = writer.book.add_format()
    formatter = set_common_formats(formatter)
    formatter.set_font_size(12)
    formatter.set_border(1)
    formatter.set_bg_color('#CCCCCC')
    formatter.set_locked(True)
    return formatter
