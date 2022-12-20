""" Types for the models

@author: D. Batista (Terazus)
"""

from abc import ABCMeta
from datetime import datetime


class ExposureCondition(metaclass=ABCMeta):
    """ The ExposureCondition is an interface for the ExposureCondition class. """
    allowed_chemicals: list[str]
    chemicals_name: list[str]
    dose: str


class InputsToDataframes(metaclass=ABCMeta):
    """ The HarvesterInput is an interface for the HarvesterInput class. """
    partner: str
    organism: str
    exposure_batch: str
    replicate4control: int
    replicate_blank: int
    start_date: datetime
    end_date: datetime
    exposure_conditions: list[ExposureCondition]
    timepoints: int
    replicate4exposure: int
    replicate4control: int
    vehicle: str
