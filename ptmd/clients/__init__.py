""" This module provides all functions needed to interact with the external storage.
At the moment it only provides Google Drive support through the pydrive2 to connect to the drive and create the
necessary directories/folders and files.

@author: D. Batista (Terazus)
"""

from .gdrive import GoogleDriveConnector
from .pretox import pull_chemicals_from_ptox_db, pull_organisms_from_ptox_db
from .file_parsers import parse_chemicals
