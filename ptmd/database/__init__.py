""" The database module provides the SQLAlchemy model (including Users and Organisations) and functions to interact
with the database such as boot(), create_organisations() and create_users().
It also provides the Base and app variables that are required to establish a connection to a database.

:author: D. Batista (Terazus)
"""

from .models import User, login_user, Organisation, Chemical
from .config import Base, app
from .create_database import boot, create_organisations, create_users, create_chemicals, create_organisms
