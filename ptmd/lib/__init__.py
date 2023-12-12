""" This module provides all functions needed to interact with the external storage.
At the moment it only provides Google Drive support through the pydrive2 to connect to the drive and create the
necessary directories/folders and files.
"""

from .gdrive import GoogleDriveConnector
from .creator import DataframeCreator
from .excel import save_to_excel
from .updater import BatchUpdater, BatchError
