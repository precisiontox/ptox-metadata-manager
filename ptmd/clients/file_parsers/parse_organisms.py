from json import load

from ptmd.const import ORGANISMS_FILEPATH


def parse_organisms(filepath: str = ORGANISMS_FILEPATH) -> list[dict]:
    """ Pulls the organisms from the ptox database.

    :param filepath: path to the organisms file.
    :return: a list of organisms from the ptox database.
    """
    with open(filepath, 'r') as f:
        organisms = load(f)
    return [organism for organism in organisms['organism'] if organism['ptox_biosystem_code'] != '-']
