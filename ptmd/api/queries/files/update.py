from uuid import uuid4
from os import remove, path

from flask import request, Response, jsonify
from pandas import read_excel, DataFrame, Series, concat as pd_concat

from ptmd.database import File
from ptmd.config import session
from ptmd.const import DOWNLOAD_DIRECTORY_PATH, PTX_ID_LABEL
from ptmd.lib.gdrive import GoogleDriveConnector
from ptmd.lib.excel import save_to_excel


def update_batch(file_id: int) -> tuple[Response, int]:
    batch = request.args.get('batch', None)
    if not batch:
        return jsonify({"message": "No batch given"}), 400

    file: File = File.query.filter_by(file_id=file_id).first()
    if not file:
        return jsonify({"message": "No file found"}), 404

    if file.shipped:
        return jsonify({"message": "File already shipped"}), 400

    try:
        file.batch = batch
        session.commit()

        filename: str = f'{file.name}_{uuid4()}.xlsx'
        filepath: str = path.join(DOWNLOAD_DIRECTORY_PATH, filename)
        google_drive: GoogleDriveConnector = GoogleDriveConnector()
        google_drive.download_file(file.gdrive_id, filename)
        old_batch: str = modify_batch_in_file(filepath, batch)
        google_drive.upload_file(filepath, filename.replace(old_batch, batch))
        remove(filepath)

        return jsonify({"message": "Batch updated"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"message": str(e)}), 500


def modify_batch_in_file(filepath: str, batch: str) -> str:
    general_information: DataFrame = read_excel(filepath, sheet_name="General Information")
    exposure_information: DataFrame = read_excel(filepath, sheet_name="Exposure information")

    samples: list = exposure_information.to_dict(orient='records')
    general_data: dict = general_information.to_dict(orient='records')[0]
    old_batch: str = general_data['exposure_batch']
    general_data['exposure_batch'] = batch

    new_exposure_information: DataFrame = DataFrame(columns=exposure_information.columns)
    new_general_information: DataFrame = DataFrame(columns=general_information.columns)
    general_info_series: Series = Series([val for key, val in general_data.items()],
                                         index=new_general_information.columns)
    new_general_information = pd_concat([new_general_information, general_info_series.to_frame().T],
                                        ignore_index=True, sort=False)

    for sample in samples:
        identifier_array = list(sample[PTX_ID_LABEL])
        identifier_array[1:3] = batch
        sample[PTX_ID_LABEL] = ''.join(identifier_array)
        series: Series = Series([val for key, val in sample.items()], index=new_exposure_information.columns)
        new_exposure_information = pd_concat([new_exposure_information, series.to_frame().T],
                                             ignore_index=True, sort=False)
    save_to_excel((new_exposure_information, new_general_information), filepath)
    return old_batch
