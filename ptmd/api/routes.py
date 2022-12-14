""" This module contains the API routes

@author: D. Batista (Terazus)
"""

from flask_jwt_extended import jwt_required

from ptmd.database import app
from .queries import login as login_user, get_me, create_gdrive_file


@app.route("/api/login", methods=["POST"])
def login():
    """ The login route """
    return login_user()


@app.route("/api/me", methods=["GET"])
@jwt_required()
def me():
    """ Get the current user"""
    return get_me()


@app.route('/api/create_file', methods=['POST'])
@jwt_required()
def create_file():
    """ Create and saves the spreadsheet in the Google Drive """
    return create_gdrive_file()
