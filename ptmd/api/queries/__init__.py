""" This module contains all the queries run by the API endpoints.

@author: D. Batista (Terazus)
"""

from .create_gdrive_file import CreateGDriveFile
from .core import get_organisms, get_chemicals, create_gdrive_file, get_organisations
from .users import create_user, change_password, get_me, login
