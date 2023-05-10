""" This module provide constants for the ptmd package. """
from os import path
from json import loads
from collections import namedtuple

from dotenv import dotenv_values

ReplicateBlankRange: namedtuple = namedtuple('ReplicateBlankRange', ['min', 'max'])

# Set files and folders path of important resources
ROOT_PATH: str = path.abspath(path.dirname(__file__))
DATA_PATH: str = path.join(ROOT_PATH, 'resources')
SCHEMAS_PATH: str = path.join(DATA_PATH, 'schemas')
INPUT_SCHEMA_PATH: str = path.join(SCHEMAS_PATH, 'inputs2dataframes.json')
EXPOSURE_SCHEMA_PATH: str = path.join(SCHEMAS_PATH, 'exposure_schema.json')
EXPOSURE_INFORMATION_SCHEMA_FILEPATH: str = path.join(SCHEMAS_PATH, 'exposure_information_sheet_schema.json')
PARTNERS_LONGNAME_PATH: str = path.join(DATA_PATH, 'data', 'partners.json')
CHEMICALS_FILEPATH: str = path.join(DATA_PATH, 'data', 'chemicals.xlsx')
ORGANISMS_FILEPATH: str = path.join(DATA_PATH, 'data', 'organisms.json')

# Load the schemas controlling the input data
with open(INPUT_SCHEMA_PATH, 'r') as f:
    INPUT_SCHEMA: dict = loads(f.read())
with open(EXPOSURE_SCHEMA_PATH, 'r') as f:
    EXPOSURE_SCHEMA: dict = loads(f.read())
with open(PARTNERS_LONGNAME_PATH, 'r') as f:
    PARTNERS_LONGNAME: dict = loads(f.read())

# Get the requirements of the input data extracted from the schemas
ALLOWED_PARTNERS: list[str] = INPUT_SCHEMA['properties']['partner']['enum']
ALLOWED_EXPOSURE_BATCH: str = INPUT_SCHEMA['properties']['exposure_batch']['pattern']
EXPOSURE_BATCH_MAX_LENGTH: int = INPUT_SCHEMA['properties']['exposure_batch']['maxLength']
REPLICATES_EXPOSURE_MIN: int = INPUT_SCHEMA['properties']['replicates4exposure']['minimum']
REPLICATES_CONTROL_MIN: int = INPUT_SCHEMA['properties']['replicates4control']['minimum']
ALLOWED_DOSE_VALUES: list[str] = EXPOSURE_SCHEMA['properties']['dose']['enum']
ALLOWED_VEHICLES: list[str] = INPUT_SCHEMA['properties']['vehicle']['enum']
TIMEPOINTS_MIN: int = INPUT_SCHEMA['properties']['timepoints']['items']['minimum']
REPLICATES_BLANK_RANGE: ReplicateBlankRange = ReplicateBlankRange(
    INPUT_SCHEMA['properties']['replicates_blank']['minimum'],
    INPUT_SCHEMA['properties']['replicates_blank']['maximum']
)

# Get some general mapping
DOSE_MAPPING: dict = {
    0: "Z",
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
SAMPLE_SHEET_EMPTY_COLUMNS: list[str] = [
    "sampleID_label",
    "Shipment identifier",
    "Label tube / identifier",
    "box_id",
    "exposure_route",
    "operator",
    "quantity_dead_during_exposure",
    "amount_replaced_before_collection",
    "collection_order",
    "box_row",
    "box_column",
    "Mass including tube (mg)",
    "Mass excluding tube (mg)",
    "observations_notes"
]
SAMPLE_SHEET_COLUMNS: list[str] = [
    *SAMPLE_SHEET_EMPTY_COLUMNS,
    "replicate",
    "compound_name",
    "dose_code",
    "timepoint_level",
    "timepoint (hours)",
    "PrecisionTox short identifier"
]
GENERAL_SHEET_COLUMNS: list[str] = [
    "partner_id",
    "biosystem_name",
    "exposure batch",
    "control",
    "replicates",
    "blanks",
    "exposure_batch_startdate",
    "exposure_batch_enddate",
    "timepoints",
    "compound_vehicle",
]
EMPTY_FIELDS_VALUES: list[str] = [''] * len(SAMPLE_SHEET_EMPTY_COLUMNS)

# Loading .env file
CONFIG: dict = dotenv_values(path.join(ROOT_PATH, 'resources', '.env'))
SETTINGS_FILE_PATH: str = CONFIG['GOOGLE_DRIVE_SETTINGS_FILEPATH']
SITE_URL: str = CONFIG['SITE_URL']

DOWNLOAD_DIR: str = path.join(DATA_PATH, 'downloads')
