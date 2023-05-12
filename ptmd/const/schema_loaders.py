""" This module loads the JSON Schemas from the schemas directory and stores them as constants.

@Author: D. Batista (Terazus)
"""

from json import loads

from .directories import INPUT_SCHEMA_PATH, EXPOSURE_SCHEMA_PATH, PARTNERS_LONGNAME_PATH


with open(INPUT_SCHEMA_PATH, 'r') as f:
    INPUT_SCHEMA: dict = loads(f.read())
with open(EXPOSURE_SCHEMA_PATH, 'r') as f:
    EXPOSURE_SCHEMA: dict = loads(f.read())
with open(PARTNERS_LONGNAME_PATH, 'r') as f:
    PARTNERS_LONGNAME: dict = loads(f.read())
