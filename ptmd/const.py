""" This module provide constants for the ptmd package. """
from os import path
from json import loads
from collections import namedtuple

from dotenv import dotenv_values


ReplicateBlankRange: namedtuple = namedtuple('ReplicateBlankRange', ['min', 'max'])
TimepointsRange: namedtuple = namedtuple('TimepointsRange', ['min', 'max'])

ROOT_PATH: str = path.abspath(path.dirname(__file__))
INPUT_SCHEMA_PATH: str = path.join(ROOT_PATH, 'resources', 'schemas', 'inputs2dataframes.json')
EXPOSURE_SCHEMA_PATH: str = path.join(ROOT_PATH, 'resources', 'schemas', 'exposure_schema.json')
PARTNERS_LONGNAME_PATH: str = path.join(ROOT_PATH, 'resources', 'data', 'partners.json')

with open(INPUT_SCHEMA_PATH, 'r') as f:
    INPUT_SCHEMA: dict = loads(f.read())
with open(EXPOSURE_SCHEMA_PATH, 'r') as f:
    EXPOSURE_SCHEMA: dict = loads(f.read())
with open(PARTNERS_LONGNAME_PATH, 'r') as f:
    PARTNERS_LONGNAME: dict = loads(f.read())

ALLOWED_PARTNERS: list[str] = INPUT_SCHEMA['properties']['partner']['enum']
ALLOWED_EXPOSURE_BATCH: str = INPUT_SCHEMA['properties']['exposure_batch']['pattern']
EXPOSURE_BATCH_MAX_LENGTH: int = INPUT_SCHEMA['properties']['exposure_batch']['maxLength']
REPLICATES_EXPOSURE_MIN: int = INPUT_SCHEMA['properties']['replicates4exposure']['minimum']
REPLICATES_CONTROL_MIN: int = INPUT_SCHEMA['properties']['replicates4control']['minimum']
REPLICATES_BLANK_RANGE: namedtuple = ReplicateBlankRange(INPUT_SCHEMA['properties']['replicates_blank']['minimum'],
                                                         INPUT_SCHEMA['properties']['replicates_blank']['maximum'])
ALLOWED_DOSE_VALUES: list[str] = EXPOSURE_SCHEMA['properties']['dose']['enum']
ALLOWED_VEHICLES: list[str] = INPUT_SCHEMA['properties']['vehicle']['enum']
TIMEPOINTS_RANGE: namedtuple = TimepointsRange(INPUT_SCHEMA['properties']['timepoints']['minimum'],
                                               INPUT_SCHEMA['properties']['timepoints']['maximum'])

DOSE_MAPPING: dict = {
    "0": "Z",
    "BMD10": "L",
    "BMD25": "M",
    "10mg/L": "H",
}
TIME_POINT_MAPPING: dict = {
    "TP0": "S",
    "TP1": "A",
    "TP2": "B",
    "TP3": "C",
    "TP4": "D",
    "TP5": "E",
}

SAMPLE_SHEET_COLUMNS: list[str] = [
    "Shipment identifier",
    "Label tube / identifier",
    "Box No.",
    "FreezerBox identifier",
    "Sample position in box",
    "Mass including tube (mg)",
    "Mass excluding tube (mg)",
    "Additional Information",
    "replicate",
    "chemical name",
    "dose",
    "time point",
    "PrecisionTox short identifier"
]

GENERAL_SHEET_COLUMNS: list[str] = [
    "partner",
    "organism",
    "exposure batch",
    "control",
    "replicates",
    "blanks",
    "start date",
    "end date",
    "timepoints",
    "vehicle",
]

# Loading .env file
CONFIG: dict = dotenv_values(path.join(ROOT_PATH, '..', '.env'))
