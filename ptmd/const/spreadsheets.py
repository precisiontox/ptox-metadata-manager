""" This module provide constants related to the generation and validation of spreadsheets.

@author: D. Batista (Terazus)
"""
from collections import namedtuple

from .schema_loaders import INPUT_SCHEMA, EXPOSURE_SCHEMA

ReplicateBlankRange: namedtuple = namedtuple('ReplicateBlankRange', ['min', 'max'])

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

DOSE_MAPPING: dict = {
    0: "Z",
    '0': "Z",
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
