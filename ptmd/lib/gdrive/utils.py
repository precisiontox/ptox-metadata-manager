""" A small utitlise to check if a given directory already exists in the drive.
"""
from __future__ import annotations

from pydrive2.drive import GoogleDrive, GoogleDriveFileList

from .const import MIME_TYPE_FOLDER


def get_folder_id(google_drive: GoogleDrive,
                  folder_name: str,
                  parent: str = 'root') -> str | None:
    """ Finds if the directory already exists in the drive and in the given directory.

    :param google_drive: The GoogleDrive object.
    :param parent: The directory to search in.
    :param folder_name: The name of the directory to search for.
    :return: True if the directory exists, False otherwise.
    """
    query: str = f"title = '{folder_name}' and mimeType = '{MIME_TYPE_FOLDER}'"
    if parent == 'root':
        query += " and 'root' in parents"
    query += " and trashed=false"
    folders: GoogleDriveFileList = google_drive.ListFile({"q": query}).GetList()
    return None if len(folders) < 1 else folders[0]['id']


def find_files_in_folder(google_drive: GoogleDrive, folder_id: str) -> list | None:
    """ Finds all the files in the given directory and return their id and title.

    :param google_drive: The GoogleDrive object.
    :param folder_id: The directory to search in.
    :return: True if the file exists, False otherwise.
    """
    files: GoogleDriveFileList = google_drive.ListFile({"q": f"'{folder_id}' in parents and trashed=false"}).GetList()
    return None if len(files) < 1 else [{"id": file['id'], "title": file['title']} for file in files]


def get_file_information(google_drive: GoogleDrive, folder_id: str, filename: str) -> dict | None:
    """ Finds the file in the given directory and return its information.

    :param google_drive: The GoogleDrive object.
    :param folder_id: The directory to search in.
    :param filename: The name of the file to search for.
    :return: The data of the file if it exists, None otherwise.
    """
    query: str = f"title = '{filename}' and '{folder_id}' in parents and trashed=false"
    files: GoogleDriveFileList = google_drive.ListFile({"q": query}).GetList()
    return None if len(files) < 1 else files[0]
