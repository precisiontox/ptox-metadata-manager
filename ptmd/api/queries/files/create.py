""" A module to get the user input and create the corresponding Excel file in the application's Google Drive.

@author: D. Batista (Terazus)
"""
from __future__ import annotations

from os import path

from flask import request, Response, jsonify
from flask_jwt_extended import get_jwt
from sqlalchemy.orm import Session

from ptmd import Inputs2Dataframes, GoogleDriveConnector
from ptmd.utils import get_session
from ptmd.const import ROOT_PATH
from ptmd.database import Organisation, File

OUTPUT_DIRECTORY_PATH: str = path.join(ROOT_PATH, 'resources')


class CreateGDriveFile:
    """ Class that get the user input and process it to create a file in the Google Drive. """

    def __init__(self):
        """ Constructor of the class. Contains the user input. """
        self.__partner: str | None = request.json.get("partner", None)
        self.__organism: str | None = request.json.get("organism", None)
        self.__exposure_batch: str | None = request.json.get("exposure_batch", None)
        self.__replicate_blank: int | None = request.json.get("replicate_blank", None)
        self.__start_date: str | None = request.json.get("start_date", None)
        self.__end_date: str | None = request.json.get("end_date", None)
        self.__exposure_conditions: list[dict[str, list[str] | str]] = request.json.get("exposure_conditions", None)
        self.__replicate4control: int | None = request.json.get("replicate4control", None)
        self.__replicate4exposure: int | None = request.json.get("replicate4exposure", None)
        self.__timepoints: list[int] | None = request.json.get("timepoints", None)
        self.__vehicle: str | None = request.json.get("vehicle", None)

    def generate_file(self, session: Session, user: int) -> dict[str, str]:
        """ Method to process the user input and create a file in the Google Drive.

        :param session: SQLAlchemy session
        :param user: user ID
        :return: dictionary containing the response from the Google Drive API
        """
        filename: str = f"{self.__partner}_{self.__organism}_{self.__exposure_batch}.xlsx"
        file_path: str = path.join(OUTPUT_DIRECTORY_PATH, filename)
        dataframes_generator: Inputs2Dataframes = Inputs2Dataframes(partner=self.__partner,
                                                                    organism=self.__organism,
                                                                    exposure_batch=self.__exposure_batch,
                                                                    replicate_blank=self.__replicate_blank,
                                                                    start_date=self.__start_date,
                                                                    end_date=self.__end_date,
                                                                    exposure_conditions=self.__exposure_conditions,
                                                                    replicate4control=self.__replicate4control,
                                                                    replicate4exposure=self.__replicate4exposure,
                                                                    timepoints=self.__timepoints,
                                                                    vehicle=self.__vehicle)
        dataframes_generator.save_file(file_path)
        folder_id: str = session.query(Organisation).filter_by(name=dataframes_generator.partner).first().gdrive_id
        gdrive: GoogleDriveConnector = GoogleDriveConnector()
        response: dict[str, str] = gdrive.upload_file(directory_id=folder_id, file_path=file_path, title=filename)
        dataframes_generator.delete_file()
        db_file: File = File(gdrive_id=response['id'],
                             name=response['title'],
                             organisation_name=self.__partner,
                             user_id=user,
                             batch=self.__exposure_batch,
                             session=session,
                             organism_name=self.__organism)
        session.add(db_file)
        session.commit()
        return response


def create_gdrive_file() -> tuple[Response, int]:
    """ Function to create a file in the Google Drive using the data provided by the user. Acquire data from a
    JSON request.

    :return: tuple containing a JSON response and a status code
    """
    session: Session = get_session()
    try:
        user_id = get_jwt()['sub']
        payload: CreateGDriveFile = CreateGDriveFile()
        response: dict[str, str] = payload.generate_file(session=session, user=user_id)
        session.close()
        return jsonify({"data": {'file_url': response['alternateLink']}}), 200
    except Exception as e:
        session.close()
        return jsonify({"message": str(e)}), 400
