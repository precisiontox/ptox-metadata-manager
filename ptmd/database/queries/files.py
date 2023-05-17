""" This module contains the database queries for the File table.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from os import remove
from uuid import uuid4

from ptmd.logger import LOGGER
from ptmd.database import User, Organisation, File
from ptmd.config import session
from ptmd.lib.gdrive import GoogleDriveConnector
from ptmd.lib.data_extractor import extract_data_from_spreadsheet


def prepare_files_data(files_data: dict) -> list[dict]:
    """ Given a dictionary of organisations containing array of files, prepare the files data to be inserted in the
    database.

    :param files_data: a dictionary of organisations containing array of files
    :return: a list of files data with the correct identifiers for organisations, authors and organisms
    """
    author: User = User.query.first()
    files: list[dict] = []

    for organisation_name, organisation_files in files_data.items():
        organisation: Organisation = Organisation.query.filter_by(name=organisation_name).first()
        if organisation_files:
            for file_data in organisation_files:
                organism_name, batch = extract_values_from_title(file_data['title'])
                connector: GoogleDriveConnector = GoogleDriveConnector()
                file_name: str = file_data['title'].replace('.xlsx', f'_{uuid4()}.xlsx')
                file_path: str = connector.download_file(file_data['id'], file_name)
                data: dict | None = extract_data_from_spreadsheet(file_path)
                if data:
                    files.append({
                        'gdrive_id': file_data['id'],
                        'name': file_data['title'],
                        'organisation_name': organisation.name,
                        'user_id': author.id,
                        'organism_name': organism_name,
                        'batch': batch,
                        **data
                    })
                remove(file_path)
    return files


def extract_values_from_title(title: str) -> tuple[str, str]:
    """ Given an XLSX file title created by the tool, extract the species name and batch code.

    :param title: the title of the XLSX file
    :return: a tuple containing the species name and batch code
    """
    clean_title: str = title.replace('.xlsx', '')
    batch: str = clean_title.split("_")[-1]
    clean_title = clean_title[0:len(clean_title) - 3]

    letter: str = clean_title[0]
    while letter != '_':
        clean_title = clean_title[1:]
        letter = clean_title[0]
    clean_title = clean_title[1:]

    return clean_title, batch


def create_files(files_data: dict) -> list[File]:
    """ Given a dictionary of organisations containing array of files, create the files in the database.

    :param files_data: a dictionary of organisations containing array of files
    :return: a list of files created in the database as File objects
    """
    LOGGER.info('Creating Files')
    prepared_data: list[dict] = prepare_files_data(files_data=files_data)
    files: list[File] = [File(**file_data) for file_data in prepared_data]
    session.add_all(files)
    session.commit()
    return files
