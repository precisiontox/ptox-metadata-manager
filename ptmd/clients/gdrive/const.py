""" This module contains the constants for the gdrive client.

@author: D. Batista (Terazus)
"""
from os import path

from ptmd.const import ROOT_PATH, CONFIG

HERE: str = path.abspath(path.dirname(__file__))

MIME_TYPE_FOLDER: str = 'application/vnd.google-apps.folder'
ROOT_FOLDER_METADATA: dict[str, str] = {
    'title': 'Pretox-Metadata-Drive',
    'mimeType': MIME_TYPE_FOLDER
}
CREDENTIALS_FILE_PATH: str = path.join(ROOT_PATH, CONFIG['GDRIVE_CREDENTIALS_FILE'])
