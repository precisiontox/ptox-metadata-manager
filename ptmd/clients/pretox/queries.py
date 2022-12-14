""" This module provides function to pull data from the ptox database using the graphQL API.

@author: D. Batista (Terazus)
"""
from requests import post
from flask import Response

from ptmd.clients.pretox.const import DEFAULT_URL, HEADERS


def pull_chemicals_from_ptox_db(endpoint: str = DEFAULT_URL) -> list[dict]:
    """ Pulls the chemicals from the ptox database.

    :param endpoint: the graphQL endpoint to pull the data from.
    :return: a list of chemicals from the ptox database.
    """
    request: str = "{ chemical(filters:{ limit: 1000 }) { common_name formula name_hash_id ptx_code }}"
    chemicals = []
    response: Response = post(endpoint, headers=HEADERS, json={"query": request}, verify=False)
    data: dict = response.json()
    if response.status_code >= 400:
        raise ConnectionError(f"Error fetching chemicals from the precision toxicology API at "
                              f"{endpoint}: {data['errors']}")
    for chemical in data['chemical']:
        chemical['common_name'] = chemical['common_name'].strip()
        if chemical['ptx_code']:
            if chemical['name_hash_id'] == '-':
                chemical['name_hash_id'] = None
            chemicals.append(chemical)
    return chemicals


def pull_organisms_from_ptox_db(endpoint: str = DEFAULT_URL) -> list[dict]:
    """ Pulls the organisms from the ptox database.

    :param endpoint: the graphQL endpoint to pull the data from.
    :return: a list of organisms from the ptox database.
    """
    request: str = "{ organism(filters:{ limit: 1000 }) { ptox_biosystem_name scientific_name ptox_biosystem_code}}"
    response: Response = post(endpoint, headers=HEADERS, json={"query": request}, verify=False)
    data: dict = response.json()
    if response.status_code >= 400:
        raise ConnectionError(f"Error fetching organisms from the precision toxicology API at "
                              f"{endpoint}: {data['errors']}")
    return [organism for organism in data['organism'] if organism['ptox_biosystem_code'] != '-']
