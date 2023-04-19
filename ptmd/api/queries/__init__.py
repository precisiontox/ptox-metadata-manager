""" This module contains all the queries run by the API endpoints.

@author: D. Batista (Terazus)
"""

from .core import get_organisms, get_chemicals, get_organisations
from .users import create_user, change_password, get_me, login
from .files import validate_file, CreateGDriveFile, register_gdrive_file, create_gdrive_file
