""" A module to create the Google Drive setting file in case it doesn't exist
"""

from os.path import exists
from yaml import dump

from ptmd.const import GOOGLE_DRIVE_SETTINGS_FILE_PATH, DOT_ENV_CONFIG
from ptmd.logger import LOGGER


def create_config_file() -> dict:
    """ A function to create the Google Drive setting file in case it doesn't exist """
    settings_data = {
        'client_config_backend': 'settings',
        'client_config': {
            'client_id': DOT_ENV_CONFIG['GOOGLE_DRIVE_CLIENT_ID'],
            'client_secret': DOT_ENV_CONFIG['GOOGLE_DRIVE_CLIENT_SECRET'],
        },
        'save_credentials': True,
        'save_credentials_backend': 'file',
        'save_credentials_file': DOT_ENV_CONFIG['GOOGLE_DRIVE_CREDENTIALS_FILEPATH'],
        'get_refresh_token': True,
        'oauth_scope': ['https://www.googleapis.com/auth/drive', 'https://mail.google.com/']
    }
    if not exists(GOOGLE_DRIVE_SETTINGS_FILE_PATH):
        LOGGER.info('Creating settings file')
        with open(GOOGLE_DRIVE_SETTINGS_FILE_PATH, 'w') as settings_file:
            dump(settings_data, settings_file, default_flow_style=False)
    return settings_data
