from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from ptmd.const import CONFIG
from ptmd.utils import initialize
from ptmd.database import Base


def get_session() -> Session:
    engine = create_engine(CONFIG['SQLALCHEMY_DATABASE_URL'])
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def init():
    session = get_session()
    initialize(users=[{'username': 'admin', 'password': 'admin', 'organisation': 'UOX'}], session=session)
