""" A simple layer to easily import constants from the top of the repository.

:author: D. Batista (Terazus)
"""

from ptmd.const import CONFIG

SQLALCHEMY_DATABASE_URI: str = CONFIG['SQLALCHEMY_DATABASE_URL']
SQLALCHEMY_SECRET_KEY: str = CONFIG['SQLALCHEMY_SECRET_KEY']
