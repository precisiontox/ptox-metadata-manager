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
    organisms: list = []
    with open(filepath, 'r') as f:
        raw_organisms = load(f)['organisms']
    for organism in raw_organisms:
        if organism['ptox_biosystem_name'] != '-' and organism['ptox_biosystem_code'] != '-':
            organisms.append({
                'scientific_name': organism['scientific_name'],
                'ptox_biosystem_name': organism['ptox_biosystem_name'],
                'ptox_biosystem_code': organism['ptox_biosystem_code']
            })
    return organisms
