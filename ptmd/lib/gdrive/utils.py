""" A small utitlise to check if a given directory already exists in the drive.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from pydrive2.drive import GoogleDrive, GoogleDriveFileList

from .const import MIME_TYPE_FOLDER


def content_exist(google_drive: GoogleDrive,
                  folder_name: str,
                  type_: str = "folder",
                  parent: str | int = 'root') -> dict[str, str] | None:
    """ Finds if the directory already exists in the drive and in the given directory.

    :param google_drive: The GoogleDrive object.
    :param parent: The directory to search in.
    :param type_: Either "file" or "folder".
    :param folder_name: The name of the directory to search for.
    :return: True if the directory exists, False otherwise.
    """
    query: str = f"title = '{folder_name}'"
    if type_ == "folder":
        query += f" and mimeType = '{MIME_TYPE_FOLDER}'"
    if parent == 'root':
        query += " and 'root' in parents"
    else:
        query += f" and '{parent}' in parents"
    query += " and trashed=false"
    folders: GoogleDriveFileList = google_drive.ListFile({"q": query}).GetList()
    if len(folders) < 1:
        return None
    return folders[0]
