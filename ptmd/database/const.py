""" A simple layer to easily import constants from the top of the repository.

:author: D. Batista (Terazus)
"""

from ptmd.const import DOT_ENV_CONFIG

SQLALCHEMY_DATABASE_URI: str = DOT_ENV_CONFIG['SQLALCHEMY_DATABASE_URL']
SQLALCHEMY_SECRET_KEY: str = DOT_ENV_CONFIG['SQLALCHEMY_SECRET_KEY']
