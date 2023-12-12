""" A module to get the user input and create the corresponding Excel file in the application's Google Drive.
"""
from __future__ import annotations

from os import path
from datetime import datetime

from flask import request, Response, jsonify
from flask_jwt_extended import get_current_user

from ptmd.lib.creator import DataframeCreator
from ptmd.lib.gdrive import GoogleDriveConnector
from ptmd.config import session
from ptmd.const import DATA_PATH as OUTPUT_DIRECTORY_PATH
from ptmd.database.models import Organisation, File, Chemical, Timepoint
from ptmd.database.queries.chemicals import get_chemicals_from_name
from ptmd.database.queries.timepoints import create_timepoints_hours
from ptmd.api.queries.utils import check_role
from ptmd.database import get_shipped_file
from ptmd.exceptions import TimepointValueError


class CreateGDriveFile:
    """ Class that get the user input and process it to create a file in the Google Drive. """

    def __init__(self) -> None:
        """ Constructor of the class. Contains the user input. """
        now: str = datetime.now().strftime("%Y-%m-%d")
        self.data: dict = {
            "partner": request.json.get("partner", None),
            "organism": request.json.get("organism", None),
            "exposure_batch": request.json.get("exposure_batch", None),
            "replicates_blank": request.json.get("replicate_blank", None),
            "start_date": request.json.get("start_date", now),
            "end_date": request.json.get("end_date", now),
            "exposure": request.json.get("exposure_conditions", None),
            "replicates4control": request.json.get("replicate4control", None),
            "replicates4exposure": request.json.get("replicate4exposure", None),
            "timepoints": request.json.get("timepoints", None),
            "vehicle": request.json.get("vehicle", None)
        }
        if get_shipped_file(self.data['organism'], self.data['exposure_batch']):
            raise ValueError(f'Batch {self.data["exposure_batch"]} for {self.data["organism"]} already exists.')

    def generate_file(self, user: int) -> dict:
        """ Method to process the user input and create a file in the Google Drive.

        :param user: user ID
        :return: dictionary containing the response from the Google Drive API
        """
        chemical_names: list[str] = []
        for exposure in self.data['exposure']:
            chemical_names += exposure['chemicals']
        chemicals: list[Chemical] = get_chemicals_from_name(chemical_names)
        timepoints: list[Timepoint] = create_timepoints_hours(self.data['timepoints'])
        filename: str = f"{self.data['partner']}_{self.data['organism']}_{self.data['exposure_batch']}.xlsx"
        file_path: str = path.join(OUTPUT_DIRECTORY_PATH, filename)
        dataframes_generator: DataframeCreator = DataframeCreator(user_input=self.data)
        dataframes_generator.save_file(file_path)
        folder_id: str = Organisation.query.filter(Organisation.name == dataframes_generator.partner).first().gdrive_id
        gdrive: GoogleDriveConnector = GoogleDriveConnector()
        response: dict[str, str] | None = gdrive.upload_file(directory_id=folder_id,
                                                             file_path=file_path,
                                                             title=filename)
        dataframes_generator.delete_file()
        if not response:
            raise Exception("An error occurred while uploading the file to the Google Drive.")

        db_file: File = File(gdrive_id=response['id'],
                             name=response['title'],
                             organisation_name=self.data['partner'],
                             user_id=user,
                             batch=self.data['exposure_batch'],
                             organism_name=self.data['organism'],
                             replicates=self.data['replicates4exposure'],
                             controls=self.data['replicates4control'],
                             blanks=self.data['replicates_blank'],
                             vehicle_name=self.data['vehicle'],
                             chemicals=chemicals,
                             timepoints=timepoints,
                             start_date=self.data['start_date'],
                             end_date=self.data['end_date'])
        session.add(db_file)
        session.commit()
        return {**dict(db_file), 'file_url': response['alternateLink']}


@check_role(role='user')
def create_gdrive_file() -> tuple[Response, int]:
    """ Function to create a file in the Google Drive using the data provided by the user. Acquire data from a
    JSON request.

    :return: tuple containing a JSON response and a status code
    """
    try:
        payload: CreateGDriveFile = CreateGDriveFile()
        response: dict = payload.generate_file(user=get_current_user().id)
        return jsonify({"data": response}), 200
    except TimepointValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": str(e)}), 400
