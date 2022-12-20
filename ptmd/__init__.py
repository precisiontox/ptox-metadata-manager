""" The ptmd module is the Precision Toxicology MetaData manager tool. It provides functions to create spreadsheets and
upload them to the Google Drive. It also provides functions to create the necessary directories/folders within that
drive.

@author: D. Batista (Terazus)
"""
from ptmd.model import Inputs2Dataframes, ExposureCondition
from ptmd.clients import GoogleDriveConnector
