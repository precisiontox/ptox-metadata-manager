""" This module provides the core functions necessary to connect to a google drive, create the necessary directorie
and upload the files to the drive.

@author: D. Batista (Terazus)
"""
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from ptmd.const import ALLOWED_PARTNERS
from ptmd.logger import LOGGER
from .const import ROOT_FOLDER_METADATA, CREDENTIALS_FILE_PATH
from .utils import directory_exist


class GoogleDriveConnector:
    """ This is the class that handle connection and interaction with the Google Drive.

    @param credential_file: The path to the credential file.
    """

    def __init__(self, credential_file: str = CREDENTIALS_FILE_PATH):
        """ Constructor for the GoogleDriveConnector class. """
        self.__credential_file = credential_file
        self.__google_auth: GoogleAuth = GoogleAuth()
        self.google_drive: GoogleDrive or None = None
        self.connect()
        LOGGER.info('Connected to Google Drive')

    def connect(self):
        """ Connect to the Google Drive.

        @return: A connected Google Drive object
        """
        if self.google_drive:
            return self.google_drive
        self.__google_auth.LoadCredentialsFile(credentials_file=self.__credential_file)
        if not self.__google_auth.credentials:
            self.__google_auth.LocalWebserverAuth()
        elif self.__google_auth.access_token_expired:
            self.__google_auth.Refresh()
        else:
            self.__google_auth.Authorize()
        self.__google_auth.SaveCredentialsFile(self.__credential_file)
        self.google_drive = GoogleDrive(self.__google_auth)

    def create_directories(self):
        """ This function will create the nested directories/folders within the Google Drive. """
        folders_ids = {
            "root_directory": directory_exist(google_drive=self.google_drive,
                                              folder_name=ROOT_FOLDER_METADATA['title']),
            "partners": {key: None for key in ALLOWED_PARTNERS}
        }
        if not folders_ids['root_directory']:
            self.google_drive.CreateFile(ROOT_FOLDER_METADATA).Upload()
            folders_ids['root_directory'] = directory_exist(google_drive=self.google_drive,
                                                            folder_name=ROOT_FOLDER_METADATA['title'])
        for partner in ALLOWED_PARTNERS:
            folders_ids['partners'][partner] = directory_exist(self.google_drive,
                                                               partner,
                                                               folders_ids['root_directory'])
            if not folders_ids['partners'][partner]:
                self.google_drive.CreateFile({
                    "title": partner,
                    "parents": [{"id": folders_ids['root_directory']}],
                    "mimeType": ROOT_FOLDER_METADATA['mimeType']
                }).Upload()
                folders_ids['partners'][partner] = directory_exist(self.google_drive,
                                                                   partner,
                                                                   folders_ids['root_directory'])
        return folders_ids
