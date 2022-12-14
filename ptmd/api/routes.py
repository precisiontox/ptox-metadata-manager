from flask_jwt_extended import jwt_required

from ptmd.database import app, login_user
from .queries import login as login_user, get_me, create_gdrive_file


@app.route("/api/login", methods=["POST"])
def login():
    return login_user()


@app.route("/api/me", methods=["GET"])
@jwt_required()
def me():
    return get_me()


@app.route('/api/create_file', methods=['POST'])
@jwt_required()
def create_file():
    return create_gdrive_file()
