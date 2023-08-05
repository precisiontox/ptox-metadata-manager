""" This module contains constants like paths to swagger data.
"""

from os import path

from ptmd.const import ROOT_PATH

SWAGGER_DATA_PATH: str = path.join(ROOT_PATH, 'resources', 'api')
FILES_DOC_PATH: str = path.join(SWAGGER_DATA_PATH, 'files')
USERS_DOC_PATH: str = path.join(SWAGGER_DATA_PATH, 'users')
CHEMICALS_DOC_PATH: str = path.join(SWAGGER_DATA_PATH, 'chemicals')
SAMPLES_DOC_PATH: str = path.join(SWAGGER_DATA_PATH, 'samples')
