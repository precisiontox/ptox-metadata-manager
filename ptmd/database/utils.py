""" Utilities for the database connection

@author: D. Batista (Terazus)
"""

print("this is naughty")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from ptmd.const import CONFIG
from ptmd.config import Base


def get_session() -> Session:
    """ Create a database session using the SQLALCHEMY_DATABASE_URL found in the .env file

    :return: a database session
    """
    engine = create_engine(CONFIG['SQLALCHEMY_DATABASE_URL'])
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
