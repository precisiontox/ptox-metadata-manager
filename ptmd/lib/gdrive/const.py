""" This module contains the constants for the gdrive client.

@author: D. Batista (Terazus)
"""
from os import path


HERE: str = path.abspath(path.dirname(__file__))

MIME_TYPE_FOLDER: str = 'application/vnd.google-apps.folder'
ROOT_FOLDER_METADATA: dict[str, str] = {
    'title': 'Pretox-Metadata-Drive',
    'mimeType': MIME_TYPE_FOLDER
}
