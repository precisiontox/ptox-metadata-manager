""" This module contains the constants for the gdrive client.

@author: D. Batista (Terazus)
"""
from os import path

HERE = path.abspath(path.dirname(__file__))

MIME_TYPE_FOLDER = 'application/vnd.google-apps.folder'
ROOT_FOLDER_METADATA = {
    'title': 'Pretox-Metadata-Drive',
    'mimeType': MIME_TYPE_FOLDER
}
CREDENTIALS_FILE_PATH = path.join(HERE, 'credentials.txt')
