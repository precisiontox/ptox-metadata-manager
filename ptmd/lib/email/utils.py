""" This module contains utility function for the email module.

@author: D. Batista (Terazus)
"""

from yaml import safe_load

from ptmd.const import SETTINGS_FILE_PATH


def get_config() -> str:
    """ Get the configuration file for the Google Drive API.

    @return: the path to the credentials file
    """
    with open(SETTINGS_FILE_PATH, 'r') as settings_file:
        settings = safe_load(settings_file)
    return settings['save_credentials_file']