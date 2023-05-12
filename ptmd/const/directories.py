""" This module provide constants related to directories used in the ptmd package.

@author: D. Batista (Terazus)
"""

from os import path

from dotenv import dotenv_values


ROOT_PATH: str = path.join(path.abspath(path.dirname(__file__)), '..')
DATA_PATH: str = path.join(ROOT_PATH, 'resources')
DOT_ENV_CONFIG: dict = dotenv_values(path.join(DATA_PATH, '.env'))
GOOGLE_DRIVE_SETTINGS_FILE_PATH: str = DOT_ENV_CONFIG['GOOGLE_DRIVE_SETTINGS_FILEPATH']
SCHEMAS_PATH: str = path.join(DATA_PATH, 'schemas')
INPUT_SCHEMA_PATH: str = path.join(SCHEMAS_PATH, 'inputs2dataframes.json')
EXPOSURE_SCHEMA_PATH: str = path.join(SCHEMAS_PATH, 'exposure_schema.json')
EXPOSURE_INFORMATION_SCHEMA_FILEPATH: str = path.join(SCHEMAS_PATH, 'exposure_information_sheet_schema.json')
CREATE_USER_SCHEMA_PATH: str = path.join(SCHEMAS_PATH, 'create_user_schema.json')
PARTNERS_LONGNAME_PATH: str = path.join(DATA_PATH, 'data', 'partners.json')
CHEMICALS_FILEPATH: str = path.join(DATA_PATH, 'data', 'chemicals.xlsx')
ORGANISMS_FILEPATH: str = path.join(DATA_PATH, 'data', 'organisms.json')
DOWNLOAD_DIRECTORY_PATH: str = path.join(DATA_PATH, 'downloads')
