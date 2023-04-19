""" This module provides all functions needed to interact with the external storage.
At the moment it only provides Google Drive support through the pydrive2 to connect to the drive and create the
necessary directories/folders and files.

@author: D. Batista (Terazus)
"""

from .gdrive import GoogleDriveConnector
from .file_parsers import parse_chemicals, parse_organisms
from .creator import Inputs2Dataframes, ExposureCondition
