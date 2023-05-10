""" A module to get the user input and create the corresponding Excel file in the application's Google Drive.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from os import path

from flask import request, Response, jsonify
from flask_jwt_extended import get_jwt

from ptmd import DataframeCreator, GoogleDriveConnector
from ptmd.config import session
from ptmd.const import ROOT_PATH
from ptmd.database import Organisation, File

OUTPUT_DIRECTORY_PATH: str = path.join(ROOT_PATH, 'resources')


class CreateGDriveFile:
    """ Class that get the user input and process it to create a file in the Google Drive. """

    def __init__(self):
        """ Constructor of the class. Contains the user input. """
        self.data: dict = {
            "partner": request.json.get("partner", None),
            "organism": request.json.get("organism", None),
            "exposure_batch": request.json.get("exposure_batch", None),
            "replicates_blank": request.json.get("replicate_blank", None),
            "start_date": request.json.get("start_date", None),
            "end_date": request.json.get("end_date", None),
            "exposure": request.json.get("exposure_conditions", None),
            "replicates4control": request.json.get("replicate4control", None),
            "replicates4exposure": request.json.get("replicate4exposure", None),
            "timepoints": request.json.get("timepoints", None),
            "vehicle": request.json.get("vehicle", None)
        }

    def generate_file(self, user: int) -> dict[str, str]:
        """ Method to process the user input and create a file in the Google Drive.

        :param user: user ID
        :return: dictionary containing the response from the Google Drive API
        """
        filename: str = f"{self.data['partner']}_{self.data['organism']}_{self.data['exposure_batch']}.xlsx"
        file_path: str = path.join(OUTPUT_DIRECTORY_PATH, filename)
        dataframes_generator: DataframeCreator = DataframeCreator(user_input=self.data)
        dataframes_generator.save_file(file_path)
        folder_id: str = Organisation.query.filter(Organisation.name == dataframes_generator.partner).first().gdrive_id
        gdrive: GoogleDriveConnector = GoogleDriveConnector()
        response: dict[str, str] = gdrive.upload_file(directory_id=folder_id, file_path=file_path, title=filename)
        dataframes_generator.delete_file()
        db_file: File = File(gdrive_id=response['id'],
                             name=response['title'],
                             organisation_name=self.data['partner'],
                             user_id=user,
                             batch=self.data['exposure_batch'],
                             organism_name=self.data['organism'])
        session.add(db_file)
        session.commit()
        return response


def create_gdrive_file() -> tuple[Response, int]:
    """ Function to create a file in the Google Drive using the data provided by the user. Acquire data from a
    JSON request.

    :return: tuple containing a JSON response and a status code
    """
    try:
        payload: CreateGDriveFile = CreateGDriveFile()
        response: dict[str, str] = payload.generate_file(user=get_jwt()['sub'])
        return jsonify({"data": {'file_url': response['alternateLink']}}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
