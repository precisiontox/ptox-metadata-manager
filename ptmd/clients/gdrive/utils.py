from pydrive2.drive import GoogleDrive

from .const import MIME_TYPE_FOLDER


def directory_exist(google_drive: GoogleDrive, folder_name, parent: str = 'root') -> str or None:
    """ Finds if the directory already exists in the drive and in the given directory.

    @param google_drive: The GoogleDrive object.
    @param parent: The directory to search in.
    @param folder_name: The name of the directory to search for.
    @return: True if the directory exists, False otherwise.
    """
    query = f"title = '{folder_name}' and mimeType='{MIME_TYPE_FOLDER}'"
    if parent == 'root':
        query += " and 'root' in parents"
    else:
        query += f" and '{parent}' in parents"
    query += " and trashed=false"
    folders = google_drive.ListFile({"q": query}).GetList()
    if len(folders) < 1:
        return None
    return folders[0]['id']
