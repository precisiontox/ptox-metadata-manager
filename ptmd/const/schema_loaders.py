""" This module loads data from JSONs and stores them as constants.

@Author: D. Batista (Terazus)
"""

from json import loads

from .directories import (
    INPUT_SCHEMA_PATH,
    EXPOSURE_SCHEMA_PATH,
    PARTNERS_LONGNAME_PATH,
    EXPOSURE_INFORMATION_SCHEMA_FILEPATH
)


with open(INPUT_SCHEMA_PATH, 'r') as f:
    INPUT_SCHEMA: dict = loads(f.read())
with open(EXPOSURE_SCHEMA_PATH, 'r') as f:
    EXPOSURE_SCHEMA: dict = loads(f.read())
with open(PARTNERS_LONGNAME_PATH, 'r') as f:
    PARTNERS_LONGNAME: dict = loads(f.read())
with open(EXPOSURE_INFORMATION_SCHEMA_FILEPATH, 'r') as f:
    EXPOSURE_INFORMATION_SCHEMA: dict = loads(f.read())
