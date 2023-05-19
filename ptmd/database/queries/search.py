""" This module contains the search queries for the database.

@author: D. Batista (Terazus)
"""

from __future__ import annotations

from ptmd.config import Base
from ptmd.database import Organisation, File, Organism, Chemical


def search_files(
    page: int = 1,
    per_page: int = 10,
    name: str | None = None,
    batch: str | None = None,
    is_valid: bool | None = None,
    replicates: dict | None = None,
    controls: dict | None = None,
    blanks: dict | None = None,
    organisation_name: str | None = None,
    organism_name: str | None = None,
    vehicle_name: str | None = None,
    chemical_name: str | None = None
) -> dict:
    """ Given input parameters, search for files in the database.

    :param page: the page number to be returned
    :param per_page: the number of files per page
    :param name: the name of the file
    :param batch: the batch code of the file
    :param is_valid: the state of the file
    :param replicates: filter on replicates, needs an operator and a value
    :param controls: filter on controls, needs an operator and a value
    :param blanks: filter on blanks, needs an operator and a value
    :param organisation_name: the name of the organisation to filter the files
    :param organism_name: the name of the organism associated with the files
    :param vehicle_name: the name of the vehicle associated with the files
    :param chemical_name: the name of the chemical associated with the files
    :return: a list of files found in the database
    """

    clauses = []

    if name:
        clauses.append(File.name.like(f'%{name}%'))
    if batch:
        clauses.append(File.batch.like(f'%{batch}%'))
    if is_valid is not None:
        if is_valid is True:
            clauses.append(File.validated == "success")
        elif is_valid is False:
            clauses.append(File.validated != "success")

    if replicates:
        clauses.append(assemble_integer_clause(filter_data=replicates, column='replicates', target=File))
    if controls:
        clauses.append(assemble_integer_clause(filter_data=controls, column='controls', target=File))
    if blanks:
        clauses.append(assemble_integer_clause(filter_data=blanks, column='blanks', target=File))

    if organisation_name:
        clauses.append(File.organisation.has(Organisation.name.like(f'%{organisation_name}%')))
    if organism_name:
        clauses.append(File.organism.has(Organism.scientific_name.like(f'%{organism_name}%')))
    if vehicle_name:
        clauses.append(File.vehicle.has(Chemical.common_name.like(f'%{vehicle_name}%')))
    if chemical_name:
        clauses.append(File.chemicals.any(Chemical.common_name.like(f'%{chemical_name}%')))

    query: Base.query = File.query.filter(*clauses).paginate(page=page, per_page=per_page)
    files: list[dict] = [dict(file) for file in query.items]
    for file in files:
        for timepoint in file['timepoints']:
            del timepoint['files']
    return {
        'data': files,
        'pagination': {
            'current_page': page,
            'next_page': page + 1 if query.has_next else None,
            'previous_previous': page - 1 if query.has_prev else None,
            'pages': query.pages,
            'per_page': per_page,
            'total': query.total
        }
    }


def assemble_integer_clause(filter_data: dict, column: str, target: Base) -> bool:
    """ Given a filter, assemble the integer clause.

    :param filter_data: the filter to be assembled
    :param column: the column to be filtered
    :param target: the target table
    :return: the assembled integer clause
    """
    operator: str = filter_data['operator']
    value: int = filter_data['value']
    if operator == 'ne':
        return target.__table__.columns[column] != value
    elif operator == 'gt':
        return target.__table__.columns[column] > value
    elif operator == 'gte':
        return target.__table__.columns[column] >= value
    elif operator == 'lt':
        return target.__table__.columns[column] < value
    elif operator == 'lte':
        return target.__table__.columns[column] <= value
    return target.__table__.columns[column] == value
