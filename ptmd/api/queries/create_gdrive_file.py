""" A module to get the user input and create the corresponding Excel file in the application's Google Drive.

@author: D. Batista (Terazus)
"""
from os import path

from flask import request
from sqlalchemy.orm import Session

from ptmd import Inputs2Dataframes, GoogleDriveConnector
from ptmd.const import ROOT_PATH
from ptmd.database import Organisation

OUTPUT_DIRECTORY_PATH: str = path.join(ROOT_PATH, 'resources')


class CreateGDriveFile:
    """ Class that get the user input and process it to create a file in the Google Drive. """

    def __init__(self):
        """ Constructor of the class. Contains the user input. """
        self.__partner: str or None = request.json.get("partner", None)
        self.__organism: str or None = request.json.get("organism", None)
        self.__exposure_batch: str or None = request.json.get("exposure_batch", None)
        self.__replicate_blank: int or None = request.json.get("replicate_blank", None)
        self.__start_date: str or None = request.json.get("start_date", None)
        self.__end_date: str or None = request.json.get("end_date", None)
        self.__exposure_conditions: list[dict[str, list[str] or str]] = request.json.get("exposure_conditions", None)
        self.__replicate4control: int or None = request.json.get("replicate4control", None)
        self.__replicate4exposure: int or None = request.json.get("replicate4exposure", None)
        self.__timepoints: int or None = request.json.get("timepoints", None)
        self.__vehicle: str or None = request.json.get("vehicle", None)

    def process_file(self, session: Session) -> dict[str, str]:
        """ Method to process the user input and create a file in the Google Drive.

        :param session: SQLAlchemy session
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
        return response
