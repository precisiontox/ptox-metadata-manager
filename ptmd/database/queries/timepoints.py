""" This module contains all queries related to timepoints.
"""
from ptmd.config import session
from ptmd.database.models import Timepoint


def create_timepoints_hours(values: list[int]) -> list[Timepoint]:
    """ Given a list of plain values, create the relevant timepoints in the database in hours

    :param values: a list of plain values
    """
    timepoints: list[Timepoint] = []
    for i, value in enumerate(values):
        timepoint = Timepoint(value=value, unit='hours', label=f'TP{i + 1}')
        session.add(timepoint)
        timepoints.append(timepoint)
    session.commit()
    return timepoints
