""" This module contains queries related to the database.

:author: D. Batista (Terazus)
"""
from .chemicals import create_chemicals, get_allowed_chemicals, get_chemical_code_mapping
from .organisms import create_organisms, get_allowed_organisms, get_organism_code
from .users import login_user, create_users
from .organisations import create_organisations
from .files import create_files, prepare_files_data, extract_values_from_title