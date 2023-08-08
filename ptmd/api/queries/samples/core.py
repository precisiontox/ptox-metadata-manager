""" Module to save samples to database.
"""
from __future__ import annotations

from uuid import uuid4
from os import remove
from json import dumps as json_dumps

from flask import Response, jsonify, request
from flask_jwt_extended import get_current_user
from pandas import ExcelFile, DataFrame
from numpy import nan

from ptmd.config import session, Base
from ptmd.lib.gdrive import GoogleDriveConnector
from ptmd.database.models import File, User, Sample, Chemical
from ptmd.api.queries.utils import check_role
from ptmd.const import PTX_ID_LABEL


class SampleGenerator:
    """ Class to generate samples from a spreadsheet and save them to the database.

    :param file_id: The id of the file to generate samples from.
    """
    compounds: dict[str, dict] = {}
    data: dict
    file: File
    filename: str
    filepath: str
    response: tuple[Response, int]
    samples: list[str]

    def __init__(self, file_id: int) -> None:
        """ Constructor method. """
        self.samples = []
        self.file_id: int = file_id
        self.get_file()

    def get_file(self) -> None:
        """ Get the file from the database. """
        file: File = File.query.filter(File.file_id == self.file_id).first()
        if not file:
            self.response = jsonify({"message": "File not found"}), 404
            return None
        current_user: User = get_current_user()
        if file.author != current_user and current_user.role != 'admin':
            self.response = jsonify({"message": "You don't have permission to access this file."}), 403
            return None
        if file.validated != 'success':
            self.response = jsonify({"message": "Samples can only be generated for valid spreadsheets"}), 400
            return None
        self.filename = file.name.replace(".xlsx", f'_{str(uuid4())}.xlsx')
        self.file = file

    def generate_samples(self) -> list[str]:
        """ Generate the samples from the spreadsheet.

        :return: A list of sample ids.
        """
        data, filepath = self.get_data()
        self.data = data
        self.filepath = filepath
        remove(filepath)
        self.save_samples()
        return self.samples

    def get_data(self) -> tuple:
        """ Get the data from the spreadsheet.

        :return: A tuple containing the data and the filepath.
        """
        connector: GoogleDriveConnector = GoogleDriveConnector()
        filepath: str = connector.download_file(file_id=self.file.gdrive_id, filename=self.filename)
        file: ExcelFile = ExcelFile(filepath, engine='openpyxl')
        general_info: DataFrame = file.parse("General Information").replace({nan: None})
        exposure_info: DataFrame = file.parse("Exposure information").replace({nan: None}).replace({"NA": None})
        general_info["exposure_batch_startdate"] = general_info["exposure_batch_startdate"].astype(str)
        general_info["exposure_batch_enddate"] = general_info["exposure_batch_enddate"].astype(str)
        exposure_info["shipment_identifier"] = exposure_info["shipment_identifier"].astype(str)
        return {
            "general_info": general_info.to_dict(orient='records')[0],
            "exposure_info": exposure_info.to_dict(orient='records')
        }, filepath

    def save_samples(self) -> None:
        """ Save the samples to the database. """
        for sample_data in self.data["exposure_info"]:
            sample_id: str = sample_data[PTX_ID_LABEL]
            compound_name: str = sample_data["compound_name"]

            if compound_name not in self.compounds:
                compound: Chemical = Chemical.query.filter(Chemical.common_name == compound_name).first()
                self.compounds[compound_name] = dict(compound) if compound else {"common_name": None}

            data: dict = {key.replace(' ', '_'): value for key, value in sample_data.items()}
            if 'CONTROL' not in compound_name and 'BLANK' not in compound_name:
                del data['compound_name']
                data['compound'] = self.compounds[compound_name]
            else:
                data['compound'] = data['compound_name']
                del data['compound_name']

            sample: Sample = Sample.query.filter(Sample.sample_id == sample_id).first()
            if sample:
                sample.data = json_dumps(data)
                self.samples.append(sample.sample_id)
            else:
                new_sample: Sample = Sample(sample_id=sample_id, file_id=self.file_id, data=data)
                session.add(new_sample)
                self.samples.append(new_sample.sample_id)

        session.commit()


@check_role(role='user')
def save_samples(file_id: int) -> tuple[Response, int]:
    """ Save the samples from a spreadsheet to the database.

    :param file_id: The id of the file to generate samples from.
    :return: A tuple containing the response and the status code.
    """
    # Process the dataframe
    sample_generator: SampleGenerator = SampleGenerator(file_id=file_id)
    if hasattr(sample_generator, "response"):
        return sample_generator.response
    return jsonify({"samples": sample_generator.generate_samples()}), 200


def get_sample(sample_id: str) -> tuple[Response, int]:
    """ Get a sample from the database.

    :param sample_id: The id of the sample to get.
    :return: A tuple containing the response and the status code.
    """
    sample: Sample = Sample.query.filter(Sample.sample_id == sample_id).first()
    if not sample:
        return jsonify({"message": f"Sample {sample_id} not found."}), 404
    return jsonify({"sample": dict(sample)}), 200


@check_role(role='user')
def get_samples() -> tuple[Response, int]:
    """ Get paginated samples from the database.

    :return: A tuple containing the response and the status code.
    """
    page: int = request.args.get('page', 1, type=int)
    per_page: int = request.args.get('per_page', 10, type=int)
    query: Base.query = Sample.query.paginate(page=page, per_page=per_page)
    return jsonify({
        'samples': [dict(sample) for sample in query.items],
        'pagination': {
            'current_page': page,
            'next_page': page + 1 if query.has_next else None,
            'previous_previous': page - 1 if query.has_prev else None,
            'pages': query.pages,
            'per_page': per_page,
            'total': query.total
        }
    }), 200
