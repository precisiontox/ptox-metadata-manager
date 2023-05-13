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
EXPOSURE_INFORMATION_SCHEMA_FILEPATH: str = path.join(SCHEMAS_PATH, 'exposure_information_sheet_schema.json')
PARTNERS_LONGNAME_PATH: str = path.join(DATA_PATH, 'data', 'partners.json')
CHEMICALS_FILEPATH: str = path.join(DATA_PATH, 'data', 'chemicals.xlsx')
ORGANISMS_FILEPATH: str = path.join(DATA_PATH, 'data', 'organisms.json')
DOWNLOAD_DIRECTORY_PATH: str = path.join(DATA_PATH, 'downloads')

# CREATOR INPUT VALIDATION SCHEMAS
CREATOR_SCHEMA_PATH: str = path.join(SCHEMAS_PATH, 'creator')
INPUT_SCHEMA_PATH: str = path.join(CREATOR_SCHEMA_PATH, 'create_dataframe_schema.json')
EXPOSURE_SCHEMA_PATH: str = path.join(CREATOR_SCHEMA_PATH, 'create_exposure_schema.json')

# API INPUT VALIDATION SCHEMAS
API_SCHEMA_PATH: str = path.join(SCHEMAS_PATH, 'api')
CREATE_USER_SCHEMA_PATH: str = path.join(API_SCHEMA_PATH, 'create_user_schema.json')
CREATE_CHEMICAL_SCHEMA_PATH: str = path.join(API_SCHEMA_PATH, 'create_chemical_schema.json')
CREATE_CHEMICALS_SCHEMA_PATH: str = path.join(API_SCHEMA_PATH, 'create_chemicals_schema.json')
