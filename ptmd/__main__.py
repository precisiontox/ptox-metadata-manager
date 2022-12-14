import sys
from argparse import ArgumentParser

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, session as sqlsession

from ptmd.utils import initialize
from ptmd.const import CONFIG
from ptmd.database import Base


def main(argv=None):
    """ Main function of the program.

    :param argv: The arguments passed to the program.
    """
    parser = ArgumentParser(description='CLI for booting pretox metadata manager', usage='python -m ptmd -r init')
    parser.add_argument('--run', '-r',
                        help='Initiate the application',
                        dest='run')
    args = parser.parse_args(argv or sys.argv[1:])
    users = [{'username': 'admin', 'password': 'admin', 'organisation': 'UOX'}]

    if args.run == 'init':
        database_url = CONFIG['SQLALCHEMY_DATABASE_URL']
        engine = create_engine(database_url)
        Base.metadata.create_all(engine)
        session: sqlsession = sessionmaker(bind=engine)
        session = session()
        return initialize(users=users, session=session)
    elif args.run == 'boot':
        pass
    else:
        raise ValueError('Invalid arguments, need to be either "init" or "boot"')


if __name__ == '__main__':
    a, b = main()
    print(a, b)
