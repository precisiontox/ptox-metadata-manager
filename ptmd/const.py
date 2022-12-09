""" This module provide constants for the ptmd package. """
from os import path
from json import loads
from collections import namedtuple

ReplicateBlankRange = namedtuple('ReplicateBlankRange', ['min', 'max'])

ROOT_PATH = path.abspath(path.dirname(__file__))
INPUT_SCHEMA_PATH = path.join(ROOT_PATH, 'resources', 'schemas', 'harvester_input_schema.json')
EXPOSURE_SCHEMA_PATH = path.join(ROOT_PATH, 'resources', 'schemas', 'exposure_schema.json')

with open(INPUT_SCHEMA_PATH, 'r') as f:
    INPUT_SCHEMA = loads(f.read())
with open(EXPOSURE_SCHEMA_PATH, 'r') as f:
    EXPOSURE_SCHEMA = loads(f.read())

ALLOWED_PARTNERS = INPUT_SCHEMA['properties']['partner']['enum']
ALLOWED_ORGANISMS = INPUT_SCHEMA['properties']['organism']['enum']
ALLOWED_EXPOSURE_BATCH = INPUT_SCHEMA['properties']['exposure_batch']['pattern']
EXPOSURE_BATCH_MAX_LENGTH = INPUT_SCHEMA['properties']['exposure_batch']['maxLength']
REPLICATES_EXPOSURE_MIN = INPUT_SCHEMA['properties']['replicates4exposure']['minimum']
REPLICATES_CONTROL_MIN = INPUT_SCHEMA['properties']['replicates4control']['minimum']
REPLICATES_BLANK_RANGE = ReplicateBlankRange(INPUT_SCHEMA['properties']['replicates_blank']['minimum'],
                                             INPUT_SCHEMA['properties']['replicates_blank']['maximum'])
ALLOWED_CHEMICAL_NAMES = EXPOSURE_SCHEMA['properties']['chemical']['enum']
ALLOWED_DOSE_VALUES = EXPOSURE_SCHEMA['properties']['doses']['items'][0]['enum']
MAX_NUMBER_OF_DOSES = EXPOSURE_SCHEMA['properties']['doses']['maxItems']

SAMPLE_SHEET_BASE_COLUMNS = [
    "Shipment identifier",
    "Label tube / identifier",
    "Box No.",
    "FreezerBoxID [SENDER TO ADD LABEL TO BOX]",
    "Sample position in box",
    "Mass including tube (mg)",
    "Mass excluding tube (mg)",
    "Additional Information",
    "replicate",
    "chemical name",
    "dose"
]

GENERAL_SHEET_BASE_COLUMNS = [
    "partner",
    "organism",
    "exposure batch",
    "replicates for control",
    "replicates blanks",
    "start date",
    "end date",
]
