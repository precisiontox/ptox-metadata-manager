""" Module for converting a file to ISA format.

@author: D. Batista (Terazus)
"""
from ptmd.database.models import File

from .core import Batch2ISA


def convert_file_to_isa(file_id: int) -> list[dict]:
    """ Convert a file to ISA format.

    :param file_id: The id of the file to convert.
    :return: A list of dictionaries containing the ISA investigations.
    """
    file: File = File.query.filter(File.file_id == file_id).first()
    if not file:
        raise FileNotFoundError(f"File with id {file_id} not found")
    if not file.received:
        raise ValueError(f"File with id {file_id} has not been received yet")
    converter: Batch2ISA = Batch2ISA(file)
    return converter.convert()
