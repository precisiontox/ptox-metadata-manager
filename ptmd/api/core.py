from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ptmd import HarvesterInput, GoogleDriveConnector
from ptmd.const import CONFIG
from ptmd.utils import initialize
from ptmd.database import app, login_user, User, Base, Organisation


@app.route("/api/login", methods=["POST"])
def login():
    session = get_session()
    try:
        username = request.json.get("username", None)
        password = request.json.get("password", None)
    except Exception:
        return jsonify({"msg": "Missing username or password"}), 400
    session.close()
    return login_user(username=username, password=password, session=session)


@app.route("/api/me", methods=["GET"])
@jwt_required()
def me():
    try:
        session = get_session()
        user_id = get_jwt()['sub']
        user = session.query(User).filter_by(id=user_id).first()
        session.close()
        return jsonify(dict(user)), 200
    except Exception:
        return jsonify({"msg": "Invalid token"}), 401


@app.route('/api/', methods=['GET'])
@jwt_required()
def index():
    return {"message": "Welcome to the precision toxicology metadata manager api"}, 200


@app.route('/api/create_file', methods=['POST'])
@jwt_required()
def create_gdrive_file():
    filepath = '../resources/test.xlsx'
    try:
        inputs = HarvesterInput(partner=request.json.get("partner", None),
                                organism=request.json.get("organism", None),
                                exposure_conditions=request.json.get("exposure_conditions", None),
                                exposure_batch=request.json.get("exposure_batch", None),
                                replicate4exposure=request.json.get("replicate4exposure", None),
                                replicate4control=request.json.get("replicate4control", None),
                                replicate_blank=request.json.get("replicate_blank", None),
                                start_date=request.json.get("start_date", None),
                                end_date=request.json.get("end_date", None))
        inputs.save_file(filepath)
        session = get_session()
        folder_id = session.query(Organisation).filter_by(name="KIT").first().gdrive_id
        session.close()
        gdrive = GoogleDriveConnector()
        url = gdrive.upload_file(directory_id=folder_id, file_path=filepath)
        inputs.delete_file()
        return jsonify({"data": {'file_url': url['alternateLink']}}), 200
    except Exception as e:
        return jsonify({"msg": str(e)}), 400


def get_session():
    engine = create_engine(CONFIG['SQLALCHEMY_DATABASE_URL'])
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def init():
    session = get_session()
    initialize(users=[{'username': 'admin', 'password': 'admin', 'organisation': 'UOX'}], session=session)


if __name__ == '__main__':
    init()
    app.run()
