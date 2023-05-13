""" This module provides the core functions necessary to connect to a google drive, create the necessary directorie
and upload the files to the drive.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from os import path

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

from ptmd.const import ALLOWED_PARTNERS, PARTNERS_LONGNAME, GOOGLE_DRIVE_SETTINGS_FILE_PATH, DOWNLOAD_DIRECTORY_PATH
from ptmd.logger import LOGGER
from .const import ROOT_FOLDER_METADATA
from .utils import get_folder_id, find_files_in_folder, get_file_information


class GoogleDriveConnector:
    """ This is the class that handle connection and interaction with the Google Drive. """
    instance_ = None
    google_drive: GoogleDrive | None

    def __new__(cls):
        """ Method to create a new instance of the GoogleDriveConnector class. """
        if not cls.instance_:
            cls.instance_ = super(GoogleDriveConnector, cls).__new__(cls)
            cls.__google_auth: GoogleAuth = GoogleAuth(settings_file=GOOGLE_DRIVE_SETTINGS_FILE_PATH)
            cls.google_drive = None
            cls.instance_.connect()
            LOGGER.info('Connected to Google Drive')
        else:
            cls.instance_.refresh_connection()
            LOGGER.info('Refreshing token to Google Drive')
        return cls.instance_

    def __init__(self):
        """ Constructor for the GoogleDriveConnector class. """
        pass

    def connect(self):
        """ Connect to the Google Drive.

        :return: A connected Google Drive object
        """
        if self.google_drive:
            return self.google_drive
        if not self.__google_auth.credentials:
            self.__google_auth.LocalWebserverAuth()
        elif self.__google_auth.access_token_expired:
            self.__google_auth.Refresh()
        else:
            self.__google_auth.Authorize()
        self.google_drive = GoogleDrive(self.__google_auth)

    def refresh_connection(self):
        """ This function will refresh the connection to the Google Drive when the token has expired. """
        if self.__google_auth.access_token_expired:
            self.__google_auth.Refresh()
            self.__google_auth.SaveCredentialsFile()
            self.google_drive = GoogleDrive(self.__google_auth)

    def create_directories(self) -> tuple[dict, dict]:
        """ This function will create the nested directories/folders within the Google Drive.

        :return: A tuple containing the ids of the folders and the ids of the files.
        """
        root_folder_id: str = get_folder_id(google_drive=self.google_drive, folder_name=ROOT_FOLDER_METADATA['title'])
        folders_ids: dict = {"root_directory": root_folder_id, "partners": {key: None for key in ALLOWED_PARTNERS}}
        files: dict = {key: None for key in ALLOWED_PARTNERS}

        # Create root directory if it does not exist
        if not root_folder_id:
            self.google_drive.CreateFile(ROOT_FOLDER_METADATA).Upload()
            folder = get_folder_id(google_drive=self.google_drive, folder_name=ROOT_FOLDER_METADATA['title'])
            folders_ids['root_directory'] = folder

        # Create partners directories if they do not exist
        for partner in ALLOWED_PARTNERS:
            folder_id: str = get_folder_id(google_drive=self.google_drive,
                                           folder_name=partner,
                                           parent=folders_ids['root_directory'])
            if folder_id:
                folders_ids['partners'][partner] = folder_id
                files_in_folder: list = find_files_in_folder(google_drive=self.google_drive, folder_id=folder_id)
                files[partner] = files_in_folder

            else:
                self.google_drive.CreateFile({
                        "title": partner,
                        "parents": [{"id": folders_ids['root_directory']}],
                        "mimeType": ROOT_FOLDER_METADATA['mimeType']
                    }).Upload()
                folders_ids['partners'][partner] = folder_id
        for partner_acronym in folders_ids['partners']:
            g_drive = folders_ids['partners'][partner_acronym]
            long_name = PARTNERS_LONGNAME[partner_acronym]
            folders_ids['partners'][partner_acronym] = {
                "g_drive": g_drive,
                "long_name": long_name
            }
        return folders_ids, files

    def upload_file(self, directory_id: str | int, file_path: str, title: str = 'SAMPLE_TEST') -> dict[str, str]:
        """ This function will upload the file to the Google Drive.

        :param directory_id: The partner organisation Google Drive folder identifier.
        :param file_path: The path to the file to be uploaded.
        :param title: The title of the file to be uploaded.
        """
        file_metadata = {
            'title': title,
            'mimeType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'parents': [{'id': directory_id}]
        }
        file = self.google_drive.CreateFile(metadata=file_metadata)
        file.SetContentFile(file_path)
        file.Upload()
        file.content.close()
        file.InsertPermission({'type': 'anyone', 'role': 'writer'})
        return get_file_information(google_drive=self.google_drive, folder_id=directory_id, filename=title)

    def download_file(self, file_id: str | int, filename: str) -> str:
        """ This function will download the file from the Google Drive.

        :param file_id: The file identifier.
        :param filename: The name of file to be downloaded.
        """
        file = self.google_drive.CreateFile({'id': file_id})
        file_path = path.join(DOWNLOAD_DIRECTORY_PATH, filename)
        file.GetContentFile(file_path)
        return file_path

    def get_filename(self, file_id: str | int) -> str:
        """ This function will return the file name.

        :param file_id: The file identifier.
        """
        file = self.google_drive.CreateFile({'id': file_id})
        return file['title']
