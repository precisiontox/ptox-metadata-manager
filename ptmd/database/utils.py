""" Utilities for the database connection

@author: D. Batista (Terazus)
"""
from pathlib import Path
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from ptmd.const import CONFIG

# Loading the database config from a config file
# located two levels up in the directory tree.
from ptmd.config import Base


def get_session() -> Session:
    """ Create a database session using the SQLALCHEMY_DATABASE_URL found in the .env file

    :return: a database session
    """
    engine = create_engine(CONFIG['SQLALCHEMY_DATABASE_URL'])
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
