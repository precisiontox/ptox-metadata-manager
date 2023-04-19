""" This module hanldes all the queries related file management:
- create a new file (and register it)
- register an existing file
- validate a registered file

@author: D. Batista (Terazus)
"""
from .validate import validate_file
from .create import CreateGDriveFile, create_gdrive_file
from .register import register_gdrive_file
