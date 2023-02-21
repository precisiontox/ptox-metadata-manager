""" A module to parse organisms from json file.

@Author: D. Batista (Terazus)
"""
from json import load

from ptmd.const import ORGANISMS_FILEPATH


def parse_organisms(filepath: str = ORGANISMS_FILEPATH) -> list[dict]:
    """ Pulls the organisms from the json file.

    :param filepath: path to the organisms file.
    :return: a list of organisms obtained from the file.
    """
    with open(filepath, 'r') as f:
        organisms = load(f)
    return [organism for organism in organisms['organism'] if organism['ptox_biosystem_code'] != '-']
