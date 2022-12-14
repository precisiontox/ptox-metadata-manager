from os import path

from flask import jsonify, request, Response
from flask_jwt_extended import get_jwt
from sqlalchemy.orm import Session

from ptmd import HarvesterInput, GoogleDriveConnector
from ptmd.const import ROOT_PATH
from ptmd.database import login_user, User, Organisation
from .utils import get_session


def login() -> tuple[Response, int]:
    session: Session = get_session()
    username: str = request.json.get('username', None)
    password: str = request.json.get('password', None)
    if not username or not password:
        session.close()
        return jsonify({"msg": "Missing username or password"}), 400
    session.close()
    return login_user(username=username, password=password, session=session)


def get_me() -> tuple[Response, int]:
    try:
        session: Session = get_session()
        user_id: int = get_jwt()['sub']
        user: User = session.query(User).filter_by(id=user_id).first()
        session.close()
        return jsonify(dict(user)), 200
    except Exception:
        return jsonify({"msg": "Invalid token"}), 401


def create_gdrive_file() -> tuple[Response, int]:
    filepath: str = path.join(ROOT_PATH, 'resources', 'test.xlsx')
    data = {
        'partner': request.json.get('partner', None),
        'organism': request.json.get('organism', None),
        'exposure_batch': request.json.get('exposure_batch', None),
        'replicate_blank': request.json.get('replicate_blank', None),
        'start_date': request.json.get('start_date', None),
        'end_date': request.json.get('end_date', None),
        'exposure_conditions': request.json.get('exposure_conditions', None),
        'replicate4control': request.json.get('replicate4control', None),
        'replicate4exposure': request.json.get('replicate4exposure', None),
    }
    try:
        inputs: HarvesterInput = HarvesterInput(**data)
        inputs.save_file(filepath)
        session: Session = get_session()
        folder_id: str = session.query(Organisation).filter_by(name=data['partner']).first().gdrive_id
        session.close()
        gdrive: GoogleDriveConnector = GoogleDriveConnector()
        response: dict = gdrive.upload_file(directory_id=folder_id, file_path=filepath)
        inputs.delete_file()
        return jsonify({"data": {'file_url': response['alternateLink']}}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400
